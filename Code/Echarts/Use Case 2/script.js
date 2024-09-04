document.addEventListener('DOMContentLoaded', function () {
    var chartDomMain = document.getElementById('main');
    var myChartMain = echarts.init(chartDomMain);
    var optionMain;
  
    // Dados iniciais para as linhas
    var dataSets = {
        data1: {dt: [1820, 1400, 931, 700, 2090, 1300, 1320], color: '#EA1F1F', name: "Data1"},
        data2: {dt: [825, 900, 1900, 950, 1200, 1600, 1320], color: '#FA72DC', name: "Data2"},
        dados3: {dt: [875, 200, 2000, 1950, 1500, 1200, 1345], color: '#FEB702', name: "Data3"},
        dados4: {dt: [1300, 500, 400, 800, 2000, 1530, 1346], color: '#1FEA89', name: "Data4"}
    };

    var Neuraspace = {
        dt: [1820, 1400, 901, 700, 2290, 1300, 1320],
        color: '#00ACC1',
        name: "Neuraspace"
    }

    var dt_time = ['Mar 07', 'Mar 08', 'Mar 09', 'Mar 10', 'Mar 11', 'Mar 12', 'Mar 13', 'Mar 14', 'Mar 15']

    var tca = 'Mar 15'
    var now = 'Mar 13'

    // Função para atualizar o gráfico principal com base nos dados selecionados nos dropdowns
    function updateMainChart() {
        var selectedData1 = document.getElementById('dropdown1').value;
        var selectedData2 = document.getElementById('dropdown2').value;

        optionMain = {
            legend: {
                data: (selectedData1 === '' || selectedData2 === '') ? ['Neuraspace','Warning Threshold', 'Alert Threshold'] : ['Neuraspace', 'Target vs Chaser','Warning Threshold', 'Alert Threshold'],
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
            dataZoom: [
                {
                    type: 'slider',
                    start: 0,
                    end: 100,
                    top: '90%',
                    handleIcon: 'M10.7,11.9H9.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4h1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                    handleSize: '50%'
                },
            ],

            series: [
                    {
                        data: Neuraspace['dt'], // Fixed data for Neuraspace
                        type: 'line',
                        color: Neuraspace['color'], // Use the color defined for Neuraspace
                        symbol: 'circle',
                        symbolSize: 8,
                        areaStyle: (selectedData1 !== '' && selectedData2 !== '') ? {} : null,
                        name: 'Neuraspace'
                    },
                    {
                        data: (selectedData1 === '' || selectedData2 === '') ? [] : calculateAbsoluteDifference(dataSets[selectedData1].dt, dataSets[selectedData2].dt),
                        type: 'line',
                        symbol: 'circle',
                        itemStyle: {
                            color: (selectedData1 === '' || selectedData2 === '') ? {} : mixcolor(selectedData1, selectedData2)
                        },
                        symbolSize: 8,
                        areaStyle: {},
                        name: 'Target vs Chaser'  
                    },
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

        myChartMain.setOption(optionMain);

    }

    
    // Função para criar os gráficos adicionais sem os dropdowns
    function createAdditionalCharts(selectedData1, selectedData2) {
        var additionalChartsContainer = document.getElementById('additionalCharts');
        additionalChartsContainer.innerHTML = ''; // Limpa os contêineres existentes

        // Define os dados para os gráficos adicionais
        var additionalDataSets = ['data1', 'data2', 'dados3', 'dados4'];

        additionalDataSets.forEach(function (dataSet1) {
            additionalDataSets.forEach(function (dataSet2) {
                var chartContainer = document.createElement('div');
                chartContainer.style.width = '200px';
                chartContainer.style.height = '200px';
                chartContainer.style.marginBottom = '20px';
                additionalChartsContainer.appendChild(chartContainer);

                var chart = echarts.init(chartContainer);

                var option = {
                    legend: {
                        data: [dataSets[dataSet1].name + ' vs ' + dataSets[dataSet2].name],
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
                    series: [
                        {
                            data: Neuraspace['dt'], // Dados fixos da Neuraspace
                            type: 'line',
                            color: Neuraspace['color'],
                            symbol: 'circle',
                            symbolSize: 8,
                            areaStyle: {},
                            name: 'Neuraspace'
                        },
                        {
                            data: calculateAbsoluteDifference(dataSets[dataSet1].dt, dataSets[dataSet2].dt),
                            type: 'line',
                            symbol: 'circle',
                            itemStyle: {
                                color: mixcolor(dataSet1, dataSet2)
                            },
                            symbolSize: 8,
                            areaStyle: {},
                            name: dataSets[dataSet1].name + ' vs ' + dataSets[dataSet2].name
                        }               ]
                };

                chart.setOption(option);
            });
        });
    }

    // Chamada da função para criar os gráficos adicionais
    createAdditionalCharts();

    function hexToRgb(hex) {
        // Remove the leading '#' if present
        hex = hex.replace(/^#/, '');

        // Parse the hexadecimal string into separate RGB components
        var bigint = parseInt(hex, 16);
        var r = (bigint >> 16) & 255;
        var g = (bigint >> 8) & 255;
        var b = bigint & 255;

        return { r: r, g: g, b: b };
    }

    function rgbToHex(r, g, b) {
        // Convert each RGB component to its hexadecimal representation
        return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    function mixcolor(dataSet1, dataSet2) {
        var color1 = dataSets[dataSet1].color;
        var color2 = dataSets[dataSet2].color;
        var rgb1 = hexToRgb(color1);
        var rgb2 = hexToRgb(color2);

        var weight = 0.6
        
        // Calculate the average of the RGB values for each color component
        var mixedColor = [
            Math.round((rgb1.r + rgb2.r * weight) / (1 + weight)), // Red component
            Math.round((rgb1.g + rgb2.g * weight) / (1 + weight)), // Green component
            Math.round((rgb1.b + rgb2.b * weight) / (1 + weight))  // Blue component
        ];

        // Convert the mixed RGB values back to hexadecimal format
        return rgbToHex(mixedColor[0], mixedColor[1], mixedColor[2]);
    }


    // Função para calcular a diferença absoluta entre dois conjuntos de dados
    function calculateAbsoluteDifference(data1, data2) {
        var absoluteDifference = [];
        for (var i = 0; i < data1.length; i++) {
            absoluteDifference.push(Math.abs(data1[i] - data2[i]));
        }
        return absoluteDifference;
    }


    // Configura os eventos de alteração nos dropdowns
    document.getElementById('dropdown1').addEventListener('change', updateMainChart);
    document.getElementById('dropdown2').addEventListener('change', updateMainChart);

    // Inicialmente, atualiza o gráfico com base no valor selecionado no primeiro dropdown
    updateMainChart();
});