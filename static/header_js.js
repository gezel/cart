<!DOCTYPE html>
<!--
European Molecular Biology Laboratory, Heidelberg.
Based an open-source graph theory library written in JavaScript. The library was developed at the Donnelly Centre at the University of Toronto. It is the successor of Cytoscape Web.
Refer to http://js.cytoscape.org/ for details.
--> 
<meta name="robots" content="noindex">
<html>
<head>
<meta name="description" content="DARET visualization" />
<link rel="stylesheet" type="text/css" href="http://cart.embl.de/static/cart-res/example.css">

<!-- #dependencies for layout algorithms -->
<script src="http://cart.embl.de/static/cart-res/cola.v3.min.js"></script>
<script src="http://cart.embl.de/static/cart-res/jquery.min.js"></script>

<meta charset=utf-8 />
<title>DARET visualization</title>
<!-- main library for network visualization.  -->
  <script src="http://cart.embl.de/static/cart-res/cytoscape.min.js"></script>
<style id="jsbin-css">
body { 
  font: 14px helvetica neue, helvetica, arial, sans-serif;
}

</style>
</head>
<body>

<!-- left panel, network visualization  -->
<div style="width:100%;">
<div style="float:left; width:80%;" id="cy"></div>



<div style="float:right; width:20%;" id="info"> <br>
<!-- images created in illustrator. check ai files in images folder. exported to jpg.  -->

                <img src="http://cart.embl.de/~det/img/drugs-logo.png"  width="120" height="45" border="0"><br>

                <img src="http://cart.embl.de/~det/img/molecular-targets-logo.png"  width="190" height="65" border="0"><br>
                <input type="checkbox" id="stitch" value="Yes" checked>STITCH
	    	<input type="checkbox" id="drugbank" value="Yes" checked>Drugbank
	    	<input type="checkbox" id="ttd" value="Yes" checked>TTD<br><br>
	    	
                <img src="http://cart.embl.de/~det/img/atc-ftc-logo.png"  width="170" height="60" border="0"><br>
	    	<input type="checkbox" id="atc" value="Yes" checked>ATC
	    	<input type="checkbox" id="ftc" value="Yes" checked>FTC<br><br>
                
	    	<img src="http://cart.embl.de/~det/img/adverse-drug-reactions-logo.png"  width="170" height="50" border="0"><br>
	    	<input type="checkbox" id="sideeffect" value="Yes" checked>Side effect
	    	<input type="checkbox" id="toxicity" value="Yes" checked>Toxicity<br><br>
                
	    	<!-- P value is log10(), which is changed with perl file as well.  -->
	    	<input style="width: 100px" class="input-range" type="range" id="pval" size=5 value="-2" min="-50" max="-2"> 10^(<span class="range-value"></span>) P value <br> 
 	   <input style="width: 100px" class="input-range2" type="range" id="odds" size=5 value="3" min="3" max="250">  <span class="range-value2"></span> Odds Ratio <br> 
 	   		<!-- button for subsetting the network.  -->
  	    	<button style="height:30px; width:90px" id="redraw-button">Redraw</button><br><br>

        
        
        
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
