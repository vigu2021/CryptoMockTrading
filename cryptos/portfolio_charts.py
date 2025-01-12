import plotly.express as px
from .models import UserCrypto,Orders

def pie_chart(user):
    current_holdings = UserCrypto.objects.filter(user = user)
    historic_holdings = Orders.objects.filter(user = user)


    # For current holdings
    crypto_names = [holding.symbol.symbol for holding in current_holdings]

    amounts = [holding.quantity * holding.avg_price for holding in current_holdings]

    current_holdings_fig = px.pie(
        names=crypto_names,  
        values=amounts,     
        title=f"{user.username.capitalize()}'s current cryptocurrency holdings"
    )

    # Customize to show percentages
    current_holdings_fig.update_traces(textinfo='percent+label')


    current_holdings_fig.update_layout(
        title_font=dict(size=20, color="white"),
        font=dict(color="white"),  # Text color
        paper_bgcolor="#121212",  # Background color of the chart
        plot_bgcolor="#121212",  # Background color of the plot area
        legend=dict(
            title_font_color="white",
            font=dict(color="white"),
            bgcolor="#1f1f1f",  # Legend background color
            bordercolor="white",
            borderwidth=1,
        ),)


    return current_holdings_fig