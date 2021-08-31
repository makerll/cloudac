<template>
  <div style="width: 100%; height: 100%" id="childpersonneltleft"></div>
</template>

<script>
export default {
  name: "childpersonneltleft",
  components: {},
  data() {
    return {};
  },
  created() {},
  mounted() {
    this.drawLine();
  },
  methods: {
    WidthAdaptive(res) {
      var windth = window.innerWidth;
      let fontSize = windth / 7680;
      return fontSize * res;
    },
    drawLine() {
      // 基于准备好的dom，初始化echarts实例
      let myChart = this.$echarts.init(document.getElementById("childpersonneltleft"));
      let option = {
        //backgroundColor: "transparent",
        grid: {
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
        },
        // graphic: {
        //   elements: [
        //     {
        //       type: "image",
        //       //z: 4,
        //       style: {
        //         image: require("../../assets/img/helloWorld/pergreenbg.png"),
        //         width: this.WidthAdaptive(232),
        //         height: this.WidthAdaptive(116),
        //       },
        //       left: "center",
        //       top: this.WidthAdaptive(24),
        //       silent: true,
        //     },
        //   ],
        // },
        series: [{
                type: 'gauge',
                startAngle: 180,
                endAngle: 0,
                min: 0,
                center: ['50%', '70%'],
				radius: '100%',
                itemStyle: {
                    color: {
        				type: 'linear',
        				x: 0,
        				y: 0,
        				x2: 1,
        				y2: 1,
        				colorStops: [{
        					offset: 0,
        					color: '#40C8A9' // 0% 处的颜色
        				}, {
        					offset: 1,
        					color: 'rgba(64, 200, 169, 0)' // 100% 处的颜色
        				}],
        			},
                },
                progress: {
                    show: true,
                    width: this.WidthAdaptive(30),
                },
                pointer: {
                    show: false,
                },
                axisLine: {
                    roundCap: false,
                    lineStyle: {
                        width: this.WidthAdaptive(30),
                    }
                },
                axisTick: {
                    show: false,
                },
                splitLine: {
                    show: false,
                },
                axisLabel: {
                    show:false,
                },
                title: {
                    offsetCenter: [0, this.WidthAdaptive(40)],
                    fontSize: this.WidthAdaptive(25),
                    fontFamily: 'Source Han Sans CN',
                    fontWeight: 400,
                    lineHeight: this.WidthAdaptive(43),
                    color: '#ffffff',
                },
                detail: {
                    color: '#ffffff',
                    fontSize: this.WidthAdaptive(35),
                    fontFamily: 'YouSheBiaoTiHei',
                    fontWeight: 400,
                    lineHeight: this.WidthAdaptive(46),
                    offsetCenter: [0, this.WidthAdaptive(-20)],
                },
                data: [{
                    value: 970,
                    name: '人员总数(人)',
                }]
            }]
      };
      window.onresize = function () {
        myChart.resize();
      };
      myChart.setOption(option);
    },
  },
};
</script>
<style scoped>
</style>

