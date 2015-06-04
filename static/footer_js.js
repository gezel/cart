   ]
  };

<!-- the network variable is loaded. -->

<!-- ################################################################### -->
<!-- initiation of network visualization -->
 $('#cy').cytoscape({
 	<!-- how much you can zoom in/out. -->
	minZoom: 0.03,
    maxZoom: 300.0,
    motionBlur: true,
    wheelSensitivity:0.05,
	<!-- after checking multiple layouts, this one looks quite good with these parameters. In the next chapter, I will use the same parameters for updating the figure as well.  -->
	layout: {
    name: 'circle',
    animate: true,
    refresh: 8,
    padding: 30,
    randomize           : true,
    nodeRepulsion       : 5000000,
    idealEdgeLength: 50,
    nodeOverlap         : 100,
    edgeElasticity      : 100,
    fit: true,
    initialTemp         :2000,
    numIter: 1000,
  },
  style: cytoscape.stylesheet()
    .selector('node')
      .css({
      	<!-- this helps us to have wider node for drugs in comparison to annotation terms. -->
      	'width': 'mapData(weight, 0, 100,0,100)',
        <!-- node shape. -->
        'shape': 'data(faveShape)',
      	'font-size': 20,
      	'padding-top': '10px',
        'padding-left': '10px',
        'padding-bottom': '10px',
        'padding-right': '10px',
        'text-valign': 'center',
        'content': 'data(label)',
        'background-color': 'data(faveColor)',
      })
    .selector('edge')
      .css({
      	<!-- fixed grey color, subject to change. -->
      	'line-color': '#A4A4A4',
          })
    .selector(':selected')
      .css({
        'line-color': 'black',
        'target-arrow-color': 'black'
      })
    .selector('.faded')
      .css({
      	<!-- this becomes active, if one of the nodes is selected. except its neightbors, all nodes will be shown as faded. -->
        'opacity': 0.3,
        'text-opacity': 0
      }),
     
  <!-- name of the computer-generated enrichment network  -->
  elements: wholenetwork,
  
  ready: function(){
    window.cy = this;
    
    // giddy up...
    <!-- ################################################################################## -->
	<!-- these functions refer to right/left click within the network. -->
    cy.elements().unselectify();
    <!-- right click, link -->
    cy.on('cxttapstart', 'node', function(){
      try { // your browser may block popups
   		 window.open( this.data('href') );
	  } catch(e){ // fall back on url change
   		 window.location.href = this.data('href'); 
  		} 
    });
    <!-- nodes are faded if not neighbors of the selected node.  -->
    cy.on('tap', 'node', function(e){
      var node = e.cyTarget; 
      var neighborhood = node.neighborhood().add(node);
      
      cy.elements().addClass('faded');
      neighborhood.removeClass('faded');
    });
    
    cy.on('tap', function(e){
      if( e.cyTarget === cy ){
        cy.elements().removeClass('faded');
      }
    });
  }
  <!-- ################################################################################## -->
  
     
});


	<!-- this function is for updating the layout with different layout algorithms. For cose and cola, there are additional parameters that were specified with the help of if conditions.  -->
	$("#cy").cy(function(){
		var cy = this;
		
		$("#layout-button").bind("click", function(){
			if($("#layout-select").val() == 'cose')
			{
				cy.layout({
				name: $("#layout-select").val(),
				padding: 30,
			    randomize           : true,
			    animate: true,
			    refresh: 8,
			    nodeRepulsion       : 5000000,
			    idealEdgeLength: 50,
			    nodeOverlap         : 100,
			    edgeElasticity      : 100,
			    fit: true,
			    initialTemp         :2000,
			    numIter: 1000});
			}
			if($("#layout-select").val() == 'cola')
			  {
				cy.layout({
				name: $("#layout-select").val(),
				padding: 10,
			    randomize : true});
			}
			<!--  the name can be directly used as the name of the layout algorithm  -->
			if(($("#layout-select").val() != 'cose')&&($("#layout-select").val() != 'cola'))
			{
			cy.layout({
				name: $("#layout-select").val()
			});
			}
			<!-- after layout, we need to fit to the whole screen. circle is much bigger in comparison to other options, for example.  -->
			cy.fit(cy.$('#j, #e'));
		});
	});
	<!-- the sole purpose of this function is to get subset of the network, either baesd on db type or pval,Odds ratio criteria.  -->
	$("#cy").cy(function(){
		$("#redraw-button").bind("click", function(){
			   <!-- In each case, we reinitiate all the network and remove nodes that are unselected.  -->
			   cy.load(wholenetwork);
			   <!-- unchecked boxes will be removed from the network.  -->
			   <!-- Here, the names should match what is specificied from the file. This filtering is only applied to annotation terms while drugs were all retained. In the next step (below), we will remove drugs (nodes) with 0 degree.    -->
			   if(!($("#stitch").is(':checked')))
			   {
			   		 cy.remove("node[db = 'STITCH']"); 
			   }
			   if(!($("#drugbank").is(':checked')))
			   {
			   		 cy.remove("node[db = 'DrugBank']"); 
			   }
			   if(!($("#ttd").is(':checked')))
			   {
			   		 cy.remove("node[db = 'TTD']"); 
			   }
			   if(!($("#atc").is(':checked')))
			   {
			   		 cy.remove("node[db = 'ATC']"); 
			   }
			   if(!($("#ftc").is(':checked')))
			   {
			   		 cy.remove("node[db = 'ChEMBL-FTC']"); 
			   }

                            if(!($("#sideeffect").is(':checked')))
			   {
			   		 cy.remove("node[db = 'SIDER']"); 
			   }
			   if(!($("#toxicity").is(':checked')))
			   {
			   		 cy.remove("node[db = 'DrugMatrix']"); 
			   }
                           cy.remove("node[[degree < 1]]")
			   <!-- filtering based on pval, there is no magic, here, i try to concatenate strings.  -->
//			   var str1 = "node[pval > ";
//			   var str2 = "]";
//			   var res = str1.concat($("#pval").val() ,str2);
//                           var pval_sam = $("#pval_sam").val()
                           
//                           var res_sam = "node[pval > " + pval_sam + "]"
			   //cy.remove(res);
                           
//                           alert("pval bar : " + res + "\npval sam: " + res_sam)
//                           cy.remove(res_sam)
			   <!--  filtering based on Odds ratio. -->
			   //var str3 = "node[odds < ";
			   //var res2 = str3.concat($("#odds").val() ,str2);
			   //cy.remove(res2);	 
			   <!-- removing all the nodes whose degree is 0.  -->
			   //cy.remove("node[[degree=0]]");
			 	
		});
                $("#filter-pval-button").bind("click",function(){
                    cy.load(wholenetwork);
                    var pval_sam = $("#pval_sam").val()
                    var res_sam = "node[pval > " + pval_sam + "]"
                    cy.remove(res_sam)
                    cy.remove("node[[degree < 1]]")
                });
                $("#filter-odds-button").bind("click", function(){
                    cy.load(wholenetwork);
                    var odds_sam = $("#odds_sam").val()
                    var res_sam = "node[odds < " + odds_sam + "]"
                    cy.remove(res_sam)         
                    cy.remove("node[[degree < 1]]")
                });

	}); 
});
function tuck(){
    var png64 = cy.png();
    $('#network-id').attr('src',png64)
}
</script>
</body>
</html>
