function gridData() {
    var data = new Array();
    var click = 0;
    const rows = 51;
    const columns = 51;

    // iterate for rows
    for (var row = 0; row < rows; row++) {
        data.push( new Array() );

        // iterate for cells/columns inside rows
        for (var column = 0; column < columns; column++) {
            data[row].push({
                x: column,
                y: row,
                click: click
            })
        }
    }
    return data;
}

var gridData = gridData();
// I like to log the data to the console for quick debugging
console.log(gridData);

var grid = d3.select("#grid")
    .append("svg")
    .attr("width","520px")
    .attr("height","520px");

var row = grid.selectAll(".row")
    .data(gridData)
    .enter().append("g")
    .attr("class", "row");

var column = row.selectAll(".square")
    .data(function(d) { return d; })
    .enter().append("rect")
    .attr("class","square")
    .attr("x", function(d) { return d.x * 10; })
    .attr("y", function(d) { return d.y * 10; })
    .attr("width", "10px")
    .attr("height", "10px")
    .style("fill", "#fff")
    .style("stroke", "#ddd")
    .on('click', function(d) {
       d.click ++;
       if ((d.click)%4 == 0 ) { d3.select(this).style("fill","#fff"); }
       if ((d.click)%4 == 1 ) { d3.select(this).style("fill","#2C93E8"); }
       if ((d.click)%4 == 2 ) { d3.select(this).style("fill","#F56C4E"); }
       if ((d.click)%4 == 3 ) { d3.select(this).style("fill","#838690"); }
    });