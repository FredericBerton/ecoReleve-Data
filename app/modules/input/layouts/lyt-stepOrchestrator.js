define([
	'ns_stepper/lyt-stepperOrchestrator',
	//'stepper/lyt-stepperOrchestrator',

], function(StepperOrchestrator) {

	'use strict';

	return StepperOrchestrator.extend({
		
		/*==========  Next / Prev  ==========*/
		onShow: function(){
			StepperOrchestrator.prototype.onShow.apply(this, arguments);
		},
		nextStep: function(){
			var currentStep = this.steps[this.currentStep];
			if(currentStep.nextOK()) {
				this.currentStep++;
				if (this.currentStep== this.steps.length) { this.finish(); }
				else {this.toStep(this.currentStep); }
			}
		},

		prevStep: function(){
			if(this.currentStep === (this.steps.length - 1)){
				this.$el.find('#btnNext').find( 'span').text('Next');
			}
			this.currentStep === 0 ? this.currentStep : this.currentStep--;
			this.toStep(this.currentStep);
		},


	});

});
