const data = [
    { title: "Paper 1", description: "Description of Paper 1", cx: 100, cy: 100, r: 30 },
    { title: "Paper 2", description: "Description of Paper 2", cx: 300, cy: 150, r: 40 },
    { title: "Paper 3", description: "Description of Paper 3", cx: 500, cy: 200, r: 35 },
    // Add more papers as needed
  ];
  
  const container = d3.select("#container");
  const details = d3.select("#details");
  
  const svg = container.append("svg")
    .attr("width", "100%")
    .attr("height", "100%");
  
  const circles = svg.selectAll("circle")
    .data(data)
    .enter()
    .append("circle")
    .attr("cx", d => d.cx)
    .attr("cy", d => d.cy)
    .attr("r", d => d.r)
    .attr("fill", "#69b3a2")
    .on("click", (event, d) => {
      details.html(`<h3>${d.title}</h3><p>${d.description}</p>`);
    });
  