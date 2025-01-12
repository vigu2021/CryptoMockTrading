from django.shortcuts import render
from cryptos.models import CryptoSymbols
import plotly.graph_objects as go
from .models import Candlestick
from django.http import Http404



# Create your views here.
def charts_page(request):
    """
    Renders a page with links to individual cryptocurrency charts.
    """
    # Fetch all available symbols from the database
    symbols = CryptoSymbols.objects.values_list('symbol', flat=True)
    return render(request, 'charts_page.html', {'symbols': symbols})


def chart_view(request, symbol):
    """
    Renders a candlestick chart with a volume histogram for a specific symbol.
    """
    # Fetch candlestick data for the given symbol
    candlesticks = Candlestick.objects.filter(symbol__symbol=symbol)

    # If no data is found, raise a 404
    if not candlesticks.exists():
        raise Http404("No data available for the specified symbol.")

    # Extract data for the chart
    timestamps = [c.timestamp for c in candlesticks]
    opens = [c.open for c in candlesticks]
    highs = [c.high for c in candlesticks]
    lows = [c.low for c in candlesticks]
    closes = [c.close for c in candlesticks]
    volumes = [c.volume for c in candlesticks]

    # Create the candlestick chart
    fig = go.Figure()

    # Add the candlestick trace
    fig.add_trace(
        go.Candlestick(
            x=timestamps,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name="Candlesticks"
        )
    )

    # Add the volume histogram trace
    fig.add_trace(
        go.Bar(
            x=timestamps,
            y=volumes,
            name="Volume",
            marker=dict(
                color='rgba(255, 255, 0, 1)',  # Bright yellow, fully opaque
                line=dict(color='rgba(255, 215, 0, 1)', width=1)  # Gold outline
            ),
            yaxis="y2"  # Assign to secondary y-axis
        )
    )


    # Customize layout
    fig.update_layout(
        title=f'Candlestick Chart with Volume for {symbol}',
        xaxis=dict(title="Timestamp"),
        yaxis=dict(title="Price"),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        template='plotly_dark',
        xaxis_rangeslider_visible=False  # Hide the range slider
    )

    # Convert the chart to HTML
    chart_html = fig.to_html(full_html=False)

    # Render the template with the chart
    return render(request, 'chart_view.html', {'chart': chart_html, 'symbol': symbol})