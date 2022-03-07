define(
['jquery', 'echarts','echarts/chart/force'], 
function( $, ec){

    var main={
        init:function(){
            main.fore();
        },
        fore:function(){
            var myChart = ec.init(document.getElementById('main')); 
            myChart.showLoading({
                    text: '正在努力的读取数据中...',    //loading话术
            });
             $.ajax({
                url: "../graph/",
                dataType: 'json'
                })
            .done(function( data ){
                var tlink = [];
                var tnode = [];
                var onum = [];
                var onode = data.node;
                var rnode = [];
                for(var i=0;i<data.node.length;i++){
                    if(data.node[i].category===1){
                        rnode.push(data.node[i]);
                    }
                }
                var rnum = rnode.length - 1;
                var radnum = parseInt(Math.random()*rnum);
                tnode.push(rnode[radnum]);
                var olink = data.link;
                myChart.hideLoading();
                var option = {      
                                title : {
                                    text: '关系图',
                                    subtext: '数据来自新浪',
                                    x:'center',
                                    y:'top'
                                },
                                tooltip : {
                                    trigger: 'item',
                                    formatter: '{a} : {b}'
                                },
                                toolbox: {
                                    show : true,
                                    feature : {
                                        restore : {show: true},
                                        magicType: {show: true, type: ['force', 'chord']},
                                        saveAsImage : {show: true}
                                    }
                                },
                                legend: {
                                    x: 'left',
                                    data:['名称','股票']
                                },
                                series : [
                                    {
                                        type:'force',
                                        // name : "人物关系",
                                        ribbonType: false,
                                        categories : [
                                            {
                                                name: '人物'
                                            },
                                            {
                                                name: '名称'
                                            },{
                                                name: '股票'
                                            }
                                        ],
                                        itemStyle: {
                                            normal: {
                                                label: {
                                                    show: true,
                                                    textStyle: {
                                                        color: '#333'
                                                    }
                                                },
                                                nodeStyle : {
                                                    brushType : 'both',
                                                    borderColor : 'rgba(255,215,0,0.4)',
                                                    borderWidth : 1
                                                },
                                                linkStyle: {
                                                    type: 'curve'
                                                }
                                            },
                                            emphasis: {
                                                label: {
                                                    show: false
                                                    // textStyle: null      // 默认使用全局文本样式，详见TEXTSTYLE
                                                },
                                                nodeStyle : {
                                                    // r: 30
                                                },
                                                linkStyle : {}
                                            }
                                        },
                                        useWorker: false,
                                        minRadius : 10,
                                        maxRadius : 25,
                                        gravity: 1.5,
                                        scaling: 1.5,
                                        linkSymbol: 'arrow',
                                        roam: 'move',
                                        nodes: tnode,
                                        links : tlink
                                    }
                                ]
                                }


                            var ecConfig = require('echarts/config');
                            function focus(param) {                               
                                var data = param.data;
                                var links = option.series[0].links;
                                var nodes = option.series[0].nodes;
                                if (
                                    data.source !== undefined
                                    && data.target !== undefined
                                ) { //点击的是边
                                    var sourceNode = nodes[data.source];
                                    var targetNode = nodes[data.target];
                                    console.log("选中了边 " + sourceNode.name + ' -> ' + targetNode.name + ' (' + data.weight + ')');
                                } else { // 点击的是点
                                    console.log("选中了" + data.name + '(' + data.value + ')');

                                   
                                    for(var i = 0;i < olink.length;i++){
                                         var flag = true;
                                        if(olink[i].source===data.name && olink[i].target != data.name){
                                           
                                            tlink.push(olink[i]);
                                            for(var j=0;j<tnode.length;j++){
                                                if(tnode[j].name === olink[i].target){
                                                    flag  = false;
                                                }
                                            }
                                            if(flag){
                                                for(var k=0;k<onode.length;k++){
                                                    if(onode[k].name===olink[i].target){
                                                        tnode.push(onode[k]);
                                                    }
                                                }
                                            }
                                        }
                                        // else if(olink[i].target===data.name && olink.source != data.name){
                                        //     tlink.push(olink[i]);
                                        //     for(var j=0;j<tnode.length;j++){
                                        //         if(tnode[j].name === olink[i].source){
                                        //             flag  = false;
                                        //         }
                                        //     }
                                        //     if(flag){
                                        //         for(var k=0;k<onode.length;k++){
                                        //             if(onode[k].name===olink[i].source){
                                        //                 tnode.push(onode[k]);
                                        //             }
                                        //         }
                                        //     }
                                        // }
                                    }
                                    option.series[0].nodes = '';
                                    option.series[0].nodes = tnode;
                                    option.series[0].links = '';
                                    option.series[0].links = tlink;
                                    myChart.setOption(option);


                                }
                            }
                            myChart.on(ecConfig.EVENT.CLICK, focus);
                            myChart.setOption(option);


                    var oselect=$('<select></select>');
                    var ooption='';
                    for(var i=0;i<rnode.length;i++){
                        ooption += "<option>"+rnode[i].name+"</option>";
                    }
                    $(oselect).append(ooption);
                    $('#menu').append(oselect);
                    $('#menu').on('change','select',function(){
                        var str = $(this).val();
                        var arylink=[];
                        var arynode=[];

                        var nodeflag = true;
                        for(var i=0;i<olink.length;i++){
                            var newsflag = false;
                            if(olink[i].source===str && olink[i].target != str){
                                arylink.push(olink[i]);
                                if(nodeflag){
                                    for(var r=0;r<onode.length;r++){
                                        if(onode[r].name=== str){
                                            arynode.push(onode[r]);
                                        }
                                    }
                                    nodeflag = false;
                                }
                                
                                for(var j=0;j<arynode.length;j++){
                                    if(arynode[j].name != olink[i].target && arynode[j].name === olink[i].source){
                                        newsflag = true;
                                    }
                                }

                                if(newsflag){
                                    for(var k=0;k<onode.length;k++){
                                        if(onode[k].name === olink[i].target){
                                            arynode.push(onode[k]);
                                            console.log('a');
                                        }
                                    }
                                }
                            }
                        }
                        tnode = arynode;
                        tlink = arylink;
                        option.series[0].nodes = '';
                        option.series[0].nodes = tnode;
                        option.series[0].links = '';
                        option.series[0].links = tlink;
                        myChart.clear();
                        myChart.setOption(option);
                        console.log(arynode);
                        console.log(arylink);
                    });
                    

            });
        }
    }
    main.init();


       
 
    

});