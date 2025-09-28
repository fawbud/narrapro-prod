/**
 * JavaScript to handle dynamic location choices in event forms
 * based on the selected event type (Online, Offline, Hybrid)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Try to find elements with multiple possible IDs (for registration and edit forms)
    const eventTypeSelect = document.getElementById('event_type_select') || 
                           document.getElementById('id_event_type') ||
                           document.querySelector('select[name="event_type"]');
    const locationSelect = document.getElementById('location_select') || 
                          document.getElementById('id_location') ||
                          document.querySelector('select[name="location"]');
    
    if (!eventTypeSelect || !locationSelect) {
        console.log('Event form elements not found:', {
            eventTypeSelect: !!eventTypeSelect,
            locationSelect: !!locationSelect
        });
        return; // Elements not found, exit
    }
    
    console.log('Event form handler initialized');
    
    // Location choices for different event types
    const locationChoices = {
        'online': [
            ['zoom', 'Zoom'],
            ['google_meet', 'Google Meet'],
            ['teams', 'Microsoft Teams'],
            ['webex', 'Cisco Webex'],
            ['skype', 'Skype'],
            ['discord', 'Discord'],
            ['youtube_live', 'YouTube Live'],
            ['facebook_live', 'Facebook Live'],
            ['instagram_live', 'Instagram Live'],
            ['twitch', 'Twitch'],
            ['lainnya', 'Lainnya']
        ],
        'offline': [
            ['aceh', 'Aceh'],
            ['sumatera_utara', 'Sumatera Utara'],
            ['sumatera_selatan', 'Sumatera Selatan'],
            ['sumatera_barat', 'Sumatera Barat'],
            ['bengkulu', 'Bengkulu'],
            ['riau', 'Riau'],
            ['kepulauan_riau', 'Kepulauan Riau'],
            ['jambi', 'Jambi'],
            ['lampung', 'Lampung'],
            ['bangka_belitung', 'Bangka Belitung'],
            ['kalimantan_barat', 'Kalimantan Barat'],
            ['kalimantan_timur', 'Kalimantan Timur'],
            ['kalimantan_selatan', 'Kalimantan Selatan'],
            ['kalimantan_tengah', 'Kalimantan Tengah'],
            ['kalimantan_utara', 'Kalimantan Utara'],
            ['banten', 'Banten'],
            ['dki_jakarta', 'DKI Jakarta'],
            ['jawa_barat', 'Jawa Barat'],
            ['jawa_tengah', 'Jawa Tengah'],
            ['daerah_istimewa_yogyakarta', 'Daerah Istimewa Yogyakarta'],
            ['jawa_timur', 'Jawa Timur'],
            ['bali', 'Bali'],
            ['nusa_tenggara_timur', 'Nusa Tenggara Timur'],
            ['nusa_tenggara_barat', 'Nusa Tenggara Barat'],
            ['gorontalo', 'Gorontalo'],
            ['sulawesi_barat', 'Sulawesi Barat'],
            ['sulawesi_tengah', 'Sulawesi Tengah'],
            ['sulawesi_utara', 'Sulawesi Utara'],
            ['sulawesi_tenggara', 'Sulawesi Tenggara'],
            ['sulawesi_selatan', 'Sulawesi Selatan'],
            ['maluku_utara', 'Maluku Utara'],
            ['maluku', 'Maluku'],
            ['papua_barat', 'Papua Barat'],
            ['papua_barat_daya', 'Papua Barat Daya'],
            ['papua_tengah', 'Papua Tengah'],
            ['papua', 'Papua'],
            ['papua_selatan', 'Papua Selatan'],
            ['papua_pegunungan', 'Papua Pegunungan']
        ],
        'hybrid': [
            ['aceh', 'Aceh'],
            ['sumatera_utara', 'Sumatera Utara'],
            ['sumatera_selatan', 'Sumatera Selatan'],
            ['sumatera_barat', 'Sumatera Barat'],
            ['bengkulu', 'Bengkulu'],
            ['riau', 'Riau'],
            ['kepulauan_riau', 'Kepulauan Riau'],
            ['jambi', 'Jambi'],
            ['lampung', 'Lampung'],
            ['bangka_belitung', 'Bangka Belitung'],
            ['kalimantan_barat', 'Kalimantan Barat'],
            ['kalimantan_timur', 'Kalimantan Timur'],
            ['kalimantan_selatan', 'Kalimantan Selatan'],
            ['kalimantan_tengah', 'Kalimantan Tengah'],
            ['kalimantan_utara', 'Kalimantan Utara'],
            ['banten', 'Banten'],
            ['dki_jakarta', 'DKI Jakarta'],
            ['jawa_barat', 'Jawa Barat'],
            ['jawa_tengah', 'Jawa Tengah'],
            ['daerah_istimewa_yogyakarta', 'Daerah Istimewa Yogyakarta'],
            ['jawa_timur', 'Jawa Timur'],
            ['bali', 'Bali'],
            ['nusa_tenggara_timur', 'Nusa Tenggara Timur'],
            ['nusa_tenggara_barat', 'Nusa Tenggara Barat'],
            ['gorontalo', 'Gorontalo'],
            ['sulawesi_barat', 'Sulawesi Barat'],
            ['sulawesi_tengah', 'Sulawesi Tengah'],
            ['sulawesi_utara', 'Sulawesi Utara'],
            ['sulawesi_tenggara', 'Sulawesi Tenggara'],
            ['sulawesi_selatan', 'Sulawesi Selatan'],
            ['maluku_utara', 'Maluku Utara'],
            ['maluku', 'Maluku'],
            ['papua_barat', 'Papua Barat'],
            ['papua_barat_daya', 'Papua Barat Daya'],
            ['papua_tengah', 'Papua Tengah'],
            ['papua', 'Papua'],
            ['papua_selatan', 'Papua Selatan'],
            ['papua_pegunungan', 'Papua Pegunungan']
        ]
    };
    
    function updateLocationChoices() {
        const selectedEventType = eventTypeSelect.value;
        const currentLocationValue = locationSelect.value;
        
        console.log('Updating location choices for event type:', selectedEventType);
        
        // Clear current options
        locationSelect.innerHTML = '';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- Pilih ' + (selectedEventType === 'online' ? 'Platform' : 'Lokasi') + ' --';
        locationSelect.appendChild(defaultOption);
        
        // Add appropriate choices based on event type
        const choices = locationChoices[selectedEventType] || locationChoices['offline'];
        
        console.log('Using choices:', choices.length);
        
        choices.forEach(function(choice) {
            const option = document.createElement('option');
            option.value = choice[0];
            option.textContent = choice[1];
            
            // Maintain selection if the current value is still valid
            if (option.value === currentLocationValue) {
                option.selected = true;
            }
            
            locationSelect.appendChild(option);
        });
        
        // Update label text - try multiple selectors
        const locationLabel = document.querySelector('label[for="id_location"]') ||
                             document.querySelector('label[for="location_select"]') ||
                             document.querySelector('label[for="' + locationSelect.id + '"]');
                             
        if (locationLabel) {
            if (selectedEventType === 'online') {
                locationLabel.textContent = 'Platform Online *';
            } else {
                locationLabel.textContent = 'Lokasi/Provinsi *';
            }
        }
    }
    
    // Update location choices when event type changes
    eventTypeSelect.addEventListener('change', updateLocationChoices);
    
    // Initialize on page load
    updateLocationChoices();
});
