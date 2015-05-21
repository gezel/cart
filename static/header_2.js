
<br>
<br>
        <!-- button for subsetting the network.  -->
        <h2>Database filter</h2><br>
  	    	<button style="height:30px; width:90px" id="redraw-button">Redraw</button><br>


           <!-- <input style="width: 100px" class="input-range" type="range" id="pval" size=5 value="-2" min="-50" max="1"> 10^(<span class="range-value"></span>) P value <br> 
 	   <input style="width: 100px" class="input-range2" type="range" id="odds" size=5 value="3" min="1" max="250">  <span class="range-value2"></span> Odds Ratio <br> -->
   <br>
   <h2>Enrichment filter</h2><br>
           P value: <input style="width: 50px;" id="pval_sam" type="text" name="fname" hspace="30"> <button style="height:20px; width:60px" id="filter-pval-button">Filter</button><br>
           Odds ratio: <input style="width: 50px;" id="odds_sam" type="text" name="lname" hspace="5"> <button style="height:20px; width:60px" id="filter-odds-button">Filter</button><br>


<br>

        
        
        
        <h2>Layout</h2>
			<!-- multiple layout algorithm names/options  -->
	    	<select id="layout-select">
	    		<option value="grid">Grid</option>
	    		<option value="cose" selected>Cose</option>
	    		<option value="cola">Cola</option>
	    		<option value="circle">Circle</option>
	    		<option value="breadthfirst">Breadth first</option>
	    		<option value="null">Null</option>
	    	</select>
	    	<!-- action button for layout  -->
	    	<button style="height:30px; width:90px" id="layout-button">Apply</button>
<br>
<br>
<a id="download-button" download="CART-Network.png" onclick="generatePNG()" href="">Download PNG</a>
<script>
function generatePNG(){
 var png64 = cy.png()
$('#download-button').attr('href',png64)
}
</script>

</div>
 
</div>


<script id="jsbin-javascript">
<!-- ####################################################################################  -->

<!-- this part is just to print back the value of range inputs, on the right side.  -->

var range = $('.input-range'),
    value = $('.range-value');
var range2 = $('.input-range2'),
    value2 = $('.range-value2');

value.html(range.attr('value'));    
range.on('input', function(){
    value.html(this.value);
}); 
value2.html(range2.attr('value'));
range2.on('input', function(){
    value2.html(this.value);
}); 

<!-- end of this panel.  -->
<!-- ####################################################################################  -->


$(function(){ // on dom ready
var wholenetwork = {
    nodes: [

<!-- Here, we fill in the network usign perl/python. -->
