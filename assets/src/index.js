// Load modules
// ------------

var $ = window.$ = window.jQuery = require('jquery');
var places = require('places.js');

// Boostrap and font-awesome
global.Tether = require('tether');
require('font-awesome/css/font-awesome.css');
require('bootstrap/dist/css/bootstrap.css');
require('bootstrap');

require('select2/dist/css/select2.css');
require('select2');

require('intl-tel-input');
require('intl-tel-input/build/js/utils');
require('intl-tel-input/build/css/intlTelInput.css');


// Local styles and features
// -------------------------

require('./main.css');

// Style select fields
if(document.querySelector('#id_profile__user_info-entrance_field')) {
	$('#id_profile__user_info-entrance_field').select2();
}

// Add flags to phone number fields
$('#id_1-phone_number').intlTelInput({
	'initialCountry': 'fr',
	'preferredCountries': ['fr', 'de', 'be', 'gb'],
	'nationalMode': false
})

// Autocomplete postal addresses
if(document.querySelector('#id_address__user_info-line_1')) {
	var placesAutocomplete = places({
		container: document.querySelector('#id_address__user_info-line_1'),
		type: 'address',
		templates: {
			value: function(suggestion) {
				return suggestion.name;
			}
		}
	})
	placesAutocomplete.on('change', function resultSelected(e) {
		document.querySelector('#id_address__user_info-postal_code').value = e.suggestion.postcode || '';
		document.querySelector('#id_address__user_info-city').value = e.suggestion.city || '';
		document.querySelector('#id_address__user_info-country').value = e.suggestion.country || '';
	})
}

if(document.querySelector('#id_address__user_info-country')) {
	places({
		container: document.querySelector('#id_address__user_info-country'),
		type: 'country',
		templates: {
			suggestion: function(suggestion) {
				code = '<div class="d-inline-block iti-flag ' + suggestion.countryCode + '"></div> ' +
					   suggestion.highlight.name;
				console.log(code);
				return code;
			}
		}
	})
}
