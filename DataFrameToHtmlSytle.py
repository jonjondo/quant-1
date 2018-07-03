__author__ = 'lottiwang'
import pandas as pb
from IPython.display import HTML, Javascript




def highlight_last_row(s):
    return ['background-color: #FF0000' if i==len(s)-1 else '' for i in range(len(s))]

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if "SELL" in val else 'green'
    return 'color: %s' % color


def csv_to_html():
    df = pb.read_csv("us_market.csv")

    html = (
    df.style
    .applymap(color_negative_red, subset=['name'])
    .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri','align':'center', 'border-style':'solid', 'border-width':'1px','border-color': 'gray','border-spacing':'0px'})
    .set_caption("Quant From Gua")
    .render()
)
    print(html)
    with open("us.html",'w') as f:
        f.write(html)
        f.close()
        
def df_to_html(df):    
    html = (
    df.style
    .applymap(color_negative_red, subset=['operation'])
    .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri','align':'center', 'border-style':'solid', 'border-width':'1px','border-color': 'gray','border-spacing':'0px'})
    .set_caption("Quant From Gua")
    .render()
     )
    return html


























if __name__ == "__main__":
    csv_to_html()