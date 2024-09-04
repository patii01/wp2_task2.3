document.addEventListener('DOMContentLoaded', function () {
    var chartDom = document.getElementById('main');
    var myChart = echarts.init(chartDom);
    var option;

    var dataSets = {
        Neuraspace: { dt: [1820, 1400, 901, 700, 2290, 1300, 1320], color: '#00ACC1', name: "Neuraspace"},
        data1: {dt: [1820, 1400, 931, 700, 2090, 1300, 1320], color: '#EA1F1F', name: "Data1"},
        data2: {dt: [825, 900, 1900, 950, 1200, 1600, 1320], color: '#FA72DC', name: "Data2"},
        dados3: {dt: [875, 200, 2000, 1950, 1500, 1200, 1345], color: '#FEB702', name: "Data3"},
        dados4: {dt: [1300, 500, 400, 800, 2000, 1530, 1346], color: '#1FEA89', name: "Data4"}
    };

    var forecast = {
        dt: [1420, 1423, 911, 745, 2210, 1500, 1220], color: '#1FEA1F', name: "Forecast"
    }

    var dt_time = ['Mar 07', 'Mar 08', 'Mar 09', 'Mar 10', 'Mar 11', 'Mar 12', 'Mar 13', 'Mar 14', 'Mar 15']

    var tca = 'Mar 15'
    var now = 'Mar 13'

    var valorPredict = dt_time[0]

    // Função para calcular os limites da banda de confiança
    function calculateConfidenceBounds(centralValues, errors) {
        var lowerBounds = [];
        var upperBounds = [];
        for (var i = 0; i < centralValues.length; i++) {
            var lowerBound = centralValues[i] - errors[i];
            var upperBound = centralValues[i] + errors[i];
            lowerBounds.push(lowerBound);
            upperBounds.push(upperBound);
        }
        return { lowerBounds: lowerBounds, upperBounds: upperBounds};
    }
    function points_to_prediction(){
        var chartDom = document.getElementById('points');
        var myChart = echarts.init(chartDom);

        var option = {
            xAxis: {
                type: 'category',
                data: dt_time
            },
            yAxis: {
                show: false
            },
            series: [{
                type: 'scatter',
                symbol: 'circle',
                symbolSize: 8,
                //color
                itemStyle: {
                    color: '#f3d500',
                    borderColor: 'black'
                },
                data: Array(dt_time.length).fill(0)
            }]
        };

        // Defina as configurações do gráfico
        myChart.setOption(option);

        // Adicione um evento de clique às barras
        myChart.on('click', function(params) {
            // Recupere o valor clicado
            var valorSelecionado = dt_time[params.dataIndex];
            valorPredict = valorSelecionado;
            updateChart();
        });

        
    }

   points_to_prediction();


    // Função para atualizar o gráfico com base nos dados selecionados nos dropdowns
    function updateChart() {

        var selectedData1 = document.getElementById('dropdown1').value;

        var centralValues = dataSets[selectedData1];
        var errors = [50, 60, 70, 80, 90, 100, 110];

        // Calculate index of valorPredict in dt_time array
        var predictIndex = dt_time.indexOf(valorPredict);

        // Slice the forecast data and confidence bounds data from valorPredict forward
        var forecastData = forecast.dt.slice(predictIndex);
        var dt_time_copy = dt_time.slice(predictIndex);
        var confidenceBounds = calculateConfidenceBounds(forecastData, errors.slice(predictIndex));


        option = {
            legend: {
                data: ['Warning Threshold', 'Alert Threshold'],
                top: '5%',
                left: 'center'
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: dt_time
            },
            yAxis: {
                type: 'value'
            },
            tooltip: {
                trigger: 'axis'
            },
            toolbox: {
                feature: {
                    dataZoom: {
                        yAxisIndex: false,
                        title: {
                            zoom: 'Seleção',
                            back: 'Restaurar Zoom'
                        },
                        iconStyle: {
                            borderColor: '#767689',
                            borderWidth: 1,
                            color: '#767689'
                        }
                    }
                }
            },
            series: [
                {
                    type: 'line',
                    markLine: {
                        symbol: 'none',
                        lineStyle: {
                            color: 'black',
                            width: 1
                        },
                        label: {
                            show: true,
                            position: 'end',
                            formatter: 'Now'
                        },
                        data: [
                            { xAxis: now }
                        ]
                    }
                },
                {
                    type: 'line',
                    markLine: {
                        symbol: 'none',
                        lineStyle: {
                            color: 'red',
                            width: 1
                        },
                        label: {
                            show: true,
                            position: 'end',
                            formatter: 'TCA'
                        },
                        data: [
                            { xAxis: tca }
                        ]
                    }
                },
                {
                    type: 'line',
                    markLine: {
                        symbol: 'none',
                        lineStyle: {
                            color: 'red',
                            width: 1.5
                        },
                        data: [
                            { yAxis: 2000 }
                        ]
                    },
                    name: 'Alert Threshold'
                },
                {
                    type: 'line',
                    markLine: {
                        symbol: 'none',
                        lineStyle: {
                            color: '#f3d500',
                            width: 1.5
                        },
                        data: [
                            { yAxis: 500 }
                        ]
                    },
                    name: 'Warning Threshold'
                },
                {
                    type: 'line', // Ensure this type matches the type of your data series
                    markArea: {
                        itemStyle: {
                            color: (new Date(now) > new Date(tca)) ? 'rgba(255, 0, 0, 0.1)' : 'rgba(0, 255, 0, 0.1)'
                        },
                        data: [[{
                            xAxis: tca 
                        }, {
                            xAxis: now 
                        }]]
                    }
                }                     
            ]
        };

        forecast_option = {
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: dt_time_copy
            },
            yAxis: {
                type: 'value'
            },
            series: [
            {
                name: 'min',
                type: 'line',
                data: predictIndex >= 0 ? confidenceBounds.lowerBounds : [], // Display only if predictIndex is valid
                lineStyle: {
                    opacity: 0
                },
                stack: 'confidence-band',
                symbol: 'none'
            },
            {
                name: 'max',
                type: 'line',
                data: predictIndex >= 0 ? confidenceBounds.upperBounds : [], // Display only if predictIndex is valid
                lineStyle: {
                    opacity: 0
                },
                areaStyle: {
                    color: '#f3d500',
                    opacity: 0.3
                },
                stack: 'confidence-band',
                symbol: 'none'
            },
            {
                data: centralValues.dt,
                type: 'line',
                symbol: 'none',
                itemStyle: {
                        color: centralValues.color
                    }
            },
            {
                data: forecast.dt,
                type: 'scatter',
                symbol: 'circle',
                symbolSize: 8,
                itemStyle: {
                    color: '#f3d500',
                    borderColor: 'black',
                    borderWidth: 1.4
                }
                
            }]
        }

        myChart.setOption(option);
        myChart.setOption(forecast_option);
    }

    

    // Função para configurar os eventos de alteração nos dropdowns
    function setupDropdownEvents(dropdownId, updateFunction) {
        var dropdown = document.getElementById(dropdownId);

        dropdown.addEventListener('change', updateFunction);
    }

    // Configura os eventos de alteração nos dropdowns
    setupDropdownEvents('dropdown1', updateChart);

    // Inicialmente, atualiza o gráfico com base no valor selecionado no primeiro dropdown
    updateChart();
    
});
