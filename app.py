from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
import dash

app = dash.Dash(__name__)
server = app.server

# TẢI DỮ LIỆU TỪ FIRESTORE
cred = credentials.Certificate("./ltptdl1-14cee-firebase-adminsdk-qygl8-a8393b61f5.json")
appLoadData = firebase_admin.initialize_app(cred)

dbFireStore = firestore.client()
queryResults = list(dbFireStore.collection(u'20078981EDWOrdered').where(u'COUNTRY', u'==', 'USA').stream())
listQueryResult = list(map(lambda x: x.to_dict(), queryResults))
dfQueryResult = pd.DataFrame(listQueryResult)

# Tổng hợp dữ liệu
data = dfQueryResult.groupby(['YEAR_ID','QTR_ID'])['TotalProductOrdered'].sum().reset_index(name='SumProductQTRYEAR')
dfTemp = dfQueryResult.groupby(['YEAR_ID','QTR_ID'])['TotalSaleOrdered'].sum().reset_index(name='SumSaleQTRYEAR')
data = data.merge(dfTemp)
dfTemp = dfQueryResult.groupby(['YEAR_ID','QTR_ID'])['ORDERNUMBER'].size().reset_index(name='QuantityQTRYEAR')
data = data.merge(dfTemp)

data1 = dfQueryResult.groupby(['YEAR_ID','STATE'])['TotalSaleOrdered'].sum().reset_index(name='SumStateYear')
data1

data["YEAR_ID"] = data["YEAR_ID"].astype("str")
data["QTR_ID"] = data["QTR_ID"].astype("str")

# TRỰC QUAN HÓA DỮ LIỆU WEB APP
app = Dash(__name__)

figSoLuongSanPham = px.bar(data, x="YEAR_ID", y="SumProductQTRYEAR", 
barmode="group", color="QTR_ID", title='Tổng số lượng sản phẩm theo quý và năm',
labels={'YEAR_ID':'Từ năm 2003, 2004 và 2005', 'QTR_ID': 'Quý trong năm', 'SumProductQTRYEAR':'Tổng số lượng SP'})

figDoanhSo = px.pie(data, values='SumSaleQTRYEAR', names='YEAR_ID',
labels={'YEAR_ID':'Năm','SumSaleQTRYEAR':'Doanh số'},
title='Tổng doanh số theo năm')

figSoLuongHoaDon = px.sunburst(data, path=['YEAR_ID', 'QTR_ID'], values='QuantityQTRYEAR',
color='QuantityQTRYEAR',
labels={'parent':'Năm', 'labels':'Quý','QuantityQTRYEAR':'Số lượng đơn hàng'},
title='Số lượng đơn hàng theo quý và năm')

figBaiTap = px.line_polar(data1,r='SumStateYear',theta='STATE',color ='YEAR_ID',
line_close=True, color_discrete_sequence=px.colors.qualitative.D3,
title="Doanh số các năm theo tiểu bang",labels={'YEAR_ID':'Năm'})

# Data for STATE dropdown
listOptState=[{"label": "All States", "value": "ALL"}]
stateData=[
    {"label": STATE, "value": STATE}
    for STATE in np.sort(dfQueryResult.STATE.unique())]
listOptState = listOptState+stateData

@app.callback(
    [Output(component_id="soluong-graph", component_property="figure"), 
    Output("doanhso-graph", "figure"), Output("soluongdonhang-graph", "figure")],
    [Input("state-filter", "value")]
)
def update_charts(state):
    filtered_data = pd.DataFrame()
    if state != "ALL":
        mask = (
            (dfQueryResult.STATE == state)
        )
        filtered_data = dfQueryResult.loc[mask, :]
    else:
        filtered_data = dfQueryResult
# Tổng hợp lại dữ liệu
    newdata = filtered_data.groupby(['YEAR_ID','QTR_ID'])['TotalProductOrdered'].sum().reset_index(name='SumProductQTRYEAR')
    dfTemp = filtered_data.groupby(['YEAR_ID','QTR_ID'])['TotalSaleOrdered'].sum().reset_index(name='SumSaleQTRYEAR')
    newdata = newdata.merge(dfTemp)
    dfTemp = filtered_data.groupby(['YEAR_ID','QTR_ID'])['ORDERNUMBER'].size().reset_index(name='QuantityQTRYEAR')
    newdata = newdata.merge(dfTemp)
    newdata.sort_values(by=['YEAR_ID','QTR_ID'], ascending=[True, True])

    newdata["YEAR_ID"] = newdata["YEAR_ID"].astype("str")
    newdata["QTR_ID"] = newdata["QTR_ID"].astype("str")
    # Render figure again
    figSoLuongSanPham_updated = px.bar(newdata, x="YEAR_ID", y="SumProductQTRYEAR", 
    barmode="group", color="QTR_ID", title='Tổng số lượng sản phẩm theo quý và năm',
    category_orders={"QTR_ID":np.sort(newdata.QTR_ID.unique())},
    labels={'YEAR_ID':'Từ năm 2003, 2004 và 2005', 'QTR_ID': 'Quý trong năm', 'SumProductQTRYEAR':'Tổng số lượng SP'})

    figDoanhSo_updated = px.pie(newdata, values='SumSaleQTRYEAR', names='YEAR_ID',
    labels={'YEAR_ID':'Năm','SumSaleQTRYEAR':'Doanh số'},
    title='Tổng doanh số theo năm')

    figSoLuongHoaDon_updated = px.sunburst(newdata, path=['YEAR_ID', 'QTR_ID'], values='QuantityQTRYEAR',
    color='QuantityQTRYEAR',
    labels={'parent':'Năm', 'labels':'Quý','QuantityQTRYEAR':'Số lượng đơn hàng'},
    title='Số lượng đơn hàng theo quý và năm')

    return figSoLuongSanPham_updated, figDoanhSo_updated, figSoLuongHoaDon_updated

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Phân tích đơn hàng tại thị trường USA", className="header-title"
                ),
                html.P(
                    children="Phân tích khối lượng đơn hàng"
                    " theo số lượng sản phẩm và tổng doanh số"
                    " trong năm 2003, 2004 và 2005 theo từng quý",
                    className="header-description"
                ),
                html.H1(children="DHCN-20078981-Nguyễn Quyết Chiến", className="header-title")
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="STATE", className="menu-title"),
                        dcc.Dropdown(
                            id="state-filter",
                            options=listOptState,
                            value="All",
                            clearable=False,
                            className="dropdown"
                        )
                    ]
                )
            ],
            className="menu"
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                    id='soluong-graph',
                    figure=figSoLuongSanPham),
                    className="card"
                ),
                html.Div(
                    children=dcc.Graph(
                    id='doanhso-graph',
                    figure=figDoanhSo),
                    className="card"
                ),
                html.Div(
                    children=dcc.Graph(
                    id='soluongdonhang-graph',
                    figure=figSoLuongHoaDon),
                    className="card"
                ),
                 html.Div(
                    children=dcc.Graph(
                    id='baitap-graph',
                    figure=figBaiTap),
                    className="card"
                )
            ], className="wrapper")
    ])



if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

