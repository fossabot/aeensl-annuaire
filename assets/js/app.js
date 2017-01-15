var $ = window.$ = window.jQuery = require('jquery');
var places = require('places.js');

global.Tether = require('tether');
require('bootstrap');

require('intl-tel-input');
require('intl-tel-input/build/js/utils');


// Add flags to phone number fields
$('#id_1-phone_number').intlTelInput({
	'initialCountry': 'fr',
	'preferredCountries': ['fr', 'de', 'be', 'gb'],
	'nationalMode': false
})

// $("#id_1-phone_number").on("countrychange", function(e, countryData) {
// 	console.log(e, countryData)
// 	var phone = $("#id_1-phone_number"); // Only one phone number per page
// 	var number = phone.intlTelInput("getNumber");
// 	console.log(number);
// 	phone.val(number); // Update the international code
// });

// Autocomplete postal addresses
if(document.querySelector('#id_1-address_line_1')) {
	var placesAutocomplete = places({
		container: document.querySelector('#id_1-address_line_1'),
		type: 'address',
		templates: {
			value: function(suggestion) {
				return suggestion.name;
			}
		}
	})
	placesAutocomplete.on('change', function resultSelected(e) {
		// document.querySelector('#id_1-address_line_2').value = e.suggestion.administrative || '';
		document.querySelector('#id_1-postal_code').value = e.suggestion.postcode || '';
		document.querySelector('#id_1-city').value = e.suggestion.city || '';
		document.querySelector('#id_1-country').value = e.suggestion.country || '';
	})
}

if(document.querySelector('#id_1-country')) {
	places({
		container: document.querySelector('#id_1-country'),
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
