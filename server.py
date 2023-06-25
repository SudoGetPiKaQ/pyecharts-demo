from flask import Flask
from jinja2 import Environment, FileSystemLoader
from jinja2.utils import markupsafe
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Pie, Tab
from pyecharts.faker import Faker
from ExtractTransform import ExtractTransformer
import pymysql

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))

from pyecharts import options as opts
from pyecharts.charts import Bar

app = Flask(__name__, static_folder="templates")


def bar_datazoom_slider() -> Bar:
    c = Bar().set_global_opts(
        title_opts=opts.TitleOpts(title="分年代电影统计",pos_left='50%',pos_top='50px'),
        datazoom_opts=[opts.DataZoomOpts()],
    )
    for k, v in ExtractTransformer().decades_counter.items():
        c.add_xaxis(v[0]).add_yaxis(k, v[1])
    return c


def line_markpoint() -> Line:
    c = (
        Line().set_global_opts(title_opts=opts.TitleOpts(title="电影时间轴统计",pos_left='30%',pos_top='50px'))
    )
    for k, v in ExtractTransformer().year_counter_by_type.items():
        c.add_xaxis(v[0]).add_yaxis(k, v[1])
    return c


def pie_rosetype() -> Pie:
    c = (
        Pie()
        .add(
            "",
            ExtractTransformer().director_counter,
            radius=["30%", "75%"],
            center=["25%", "50%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add(
            "",
            ExtractTransformer().actor_counter,
            radius=["30%", "75%"],
            center=["75%", "50%"],
            rosetype="area",
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="演员导演统计", pos_left='10%', pos_top='100px'),)
    )
    return c


tab = Tab()
tab.add(bar_datazoom_slider(), "柱状图")
tab.add(line_markpoint(), "折线图")
tab.add(pie_rosetype(), "饼图")


@app.route("/")
def index():
    c = tab
    return markupsafe.Markup(tab.render_embed(template_name='simple_tab.html'))


if __name__ == "__main__":
    app.run()
