<!DOCTYPE html>
<!--
European Molecular Biology Laboratory, Heidelberg.
Based an open-source graph theory library written in JavaScript. The library was developed at the Donnelly Centre at the University of Toronto. It is the successor of Cytoscape Web.
Refer to http://js.cytoscape.org/ for details.
--> 
<meta name="robots" content="noindex">
<html>
<head>
<meta name="description" content="CART visualization" />
<link rel="stylesheet" type="text/css" href="http://cart.embl.de/static/cart-res/example.css">

<!-- #dependencies for layout algorithms -->
<script src="http://cart.embl.de/static/cart-res/cola.v3.min.js"></script>
<script src="http://cart.embl.de/static/cart-res/jquery.min.js"></script>

<meta charset=utf-8 />
<title>CART visualization</title>
<!-- main library for network visualization.  -->
  <script src="http://cart.embl.de/static/cart-res/cytoscape.min.js"></script>
<style id="jsbin-css">
body { 
  font: 14px helvetica neue, helvetica, arial, sans-serif;
}

</style>
</head>
<body onload="tuck()">

<!-- left panel, network visualization  -->
<div style="width:100%;">
<div style="float:left; width:80%;" id="cy"></div>



<div style="float:right; width:20%;" id="info"> <br>
<!-- images created in illustrator. check ai files in images folder. exported to jpg.  -->
                <img src="http://det.embl.de/~det/img/drugs-logo.png"  width="120" height="45" border="0"><br>
