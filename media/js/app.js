// bleh, globals and the functions that modify them.
// :TODO: find out how to do this correctly in js
var clicked_nodes = new Array();
var click_node = function(name) {
    var ind = clicked_nodes.lastIndexOf(name);
    // deselect nodes when clicked a second time
    if(ind == 0) {
        clicked_nodes.shift();
    } else if(ind == 1) {
        clicked_nodes.pop();
    } else {
        // select the node for possible operations
        if(clicked_nodes.size() == 0) {
            clicked_nodes.push(name);
        } else {
            // or becoming/replacing the second element
            clicked_nodes[1] = name;
        }
    }
    update_node_handler(clicked_nodes);
};
var update_node_handler = function(nodes) {
    $('node_zero_input').value = nodes[0];
    $('node_one_input').value = nodes[1];
    if(nodes[0]) {
        $('node_zero_display').innerHTML = nodes[0];
        $('node_zero_display').removeClassName('node_unselected')
    } else {
        $('node_zero_display').innerHTML = 'None';
        $('node_zero_display').addClassName('node_unselected')
    }
    if(nodes[1]) {
        $('node_one_display').innerHTML = nodes[1];
        $('node_one_display').removeClassName('node_unselected')
    } else {
        $('node_one_display').innerHTML = 'None';
        $('node_one_display').addClassName('node_unselected')
    }
    if(nodes.size() == 2) {
        $('node_handler_form').enable();
    } else {
        $('node_handler_form').disable();
    }
};
Event.observe(window, 'load', function() {
        //var can = new Canviz("canviz_test", "/site_media/nets/livenet.xdot");
        var can = new Canviz("canviz_test", "/nets/canviz/");
        $('node_handler_form').disable();
});
