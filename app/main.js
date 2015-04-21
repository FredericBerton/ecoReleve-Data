require.config({ 
	baseUrl: 'app',
	paths : {
		
		'tmp'					: './tmp',
		
		'app'					: 'app',
		'config'				: 'config',
		'router'				: 'router',
		'controller'			: 'controller',
		'models'				: './models',
		'collections'			: './collections',
		'templates'				: '../build/templates',
		'lyt-rootview'			: './base/rootview/lyt-rootview',
		'transition-region'		: './base/transition-region/transition-region',
		'google': './vendors/google-maps-loader',
		
		
		/*==========  NS modules  ==========*/
		'ns_modules'			: 'ns_modules',
		'ns_filter'				: 'ns_modules/ns_filter',
		'ns_form'				: 'ns_modules/ns_form',
		'ns_grid'				: 'ns_modules/ns_grid',
		'ns_map'				: 'ns_modules/ns_map',
		'ns_stepper'			: 'ns_modules/ns_stepper',

		'fancytree' : 'vendors/jquery.fancytree-all',
		'autocompTree' : 'vendors/jquery.autocompTree',
		
		
		/*==========  Bower  ==========*/
		'jquery'				: '../bower_components/jquery/jquery.min',
		'jqueryui'				: '../bower_components/jqueryui/jquery-ui.min',
		'underscore'			: '../bower_components/underscore/underscore',
		'backbone'				: '../bower_components/backbone/backbone',
		'marionette'			: '../bower_components/marionette/lib/core/backbone.marionette',
		'backbone.babysitter'	: '../bower_components/backbone.babysitter/lib/backbone.babysitter',
		'backbone.wreqr'		: '../bower_components/backbone.wreqr/lib/backbone.wreqr',
		'radio'					: '../bower_components/backbone.radio/build/backbone.radio',
		'sha1'					: '../bower_components/sha1/bin/sha1',
		'sweetAlert'			:'../bower_components/sweetalert/lib/sweet-alert.min',
		'moment'				: '../bower_components/moment/min/moment.min',
		'dateTimePicker'		: '../bower_components/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker',
		'backbone_forms'		: '../bower_components/backbone-forms/distribution.amd/backbone-forms.min',
		'backbone.paginator'	: '../bower_components/backbone.paginator/lib/backbone.paginator.min',

		'backgridSelect_all'	:'../bower_components/backgrid-select-all/backgrid-select-all.min',
		'L'						: '../bower_components/leaflet/dist/leaflet',
		'leaflet_cluster'		: '../bower_components/leaflet.markercluster/dist/leaflet.markercluster',
		'leaflet_google'		: '../bower_components/leaflet-plugins/layer/tile/Google',
		'swiper'				: '../bower_components/swiper/dist/js/swiper',
		'simplePagination'		: '../bower_components/simplePagination.js/jquery.simplePagination',
		//waiting for a new release (amd friendly)
		'backgrid'				: 'vendors/backgrid',
		'backgrid.paginator'	: 'vendors/backgrid-paginator',
	},

	shim : {
		jquery : {
			exports : '$'
		},
		jqueryui: {
			exports: 'ui'
		},
		underscore : {
			exports : '_'
		},
		backbone : {
			deps : ['jquery', 'underscore'],
			exports : 'Backbone'
		},
		marionette : {
			exports : 'Marionette'
		},
		radio : {
			exports : 'Radio'
		},
		templates :{
			deps : ['underscore'],
			exports : 'Templates',
		},
		sha1: {
			exports: 'sha1'
		},
		sweetAlert: {
			exports:'Swal'
		},
		moment : {
			exports : 'moment'
		},
		dateTimePicker : {
			exports: 'dateTimePicker'
		},
		'backbone.paginator': {
			exports: 'backbone.paginator',
		},
		backgrid: {
			exports: 'Backgrid'
		},
		'backgrid.paginator': {
			exports: 'backgrid.paginator',
		},
		backgridSelect_all : {
			deps:['backgrid'],
			exports : 'backgridSelect_all'
		},
		leaflet_cluster : {
			deps:['L'],
			exports : 'leaflet_cluster'
		},
		leaflet_google : {
			deps:['L', 'google'],
			exports : 'leaflet_google'
		},
		leaflet : {
			exports : 'L'
		},
		swiper : {
			exports : 'Swiper'
		},
		simplePagination: {
			deps : ['jquery'],
			exports : 'SimplePagination'
		},
		fancytree :  {
			deps:['jquery','jqueryui'],
			exports : 'Fancytree'
		},
		autocompTree : {
			deps:['fancytree'],
			exports : 'AutocompTree'
		},


	},
});


require(['app', 'templates'], function(app){
		app.start();
});
