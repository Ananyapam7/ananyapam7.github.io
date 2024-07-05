const data=[{title:"Paper 1",description:"Description of Paper 1",cx:100,cy:100,r:30},{title:"Paper 2",description:"Description of Paper 2",cx:300,cy:150,r:40},{title:"Paper 3",description:"Description of Paper 3",cx:500,cy:200,r:35}],container=d3.select("#container"),details=d3.select("#details"),svg=container.append("svg").attr("width","100%").attr("height","100%"),circles=svg.selectAll("circle").data(data).enter().append("circle").attr("cx",t=>t.cx).attr("cy",t=>t.cy).attr("r",t=>t.r).attr("fill","#69b3a2").on("click",(t,e)=>{details.html(`<h3>${e.title}</h3><p>${e.description}</p>`)});