/**
 * Small reusable calendar widget extracted from `mainpage.js`.
 * Exposes two globals used by existing pages:
 *  - `getCalendarSkeleton()` -> returns the HTML string for the calendar widget
 *  - `attachAppointmentsCalendar(apptsByDate, prefsByAddressString)` -> mounts behavior
 */
(function(window){
    function getCalendarSkeleton() {
        return `
            <div class="calendar-widget">
                <div class="cal-header">
                    <button id="cal-prev" class="cal-nav" aria-label="Previous month">‹</button>
                    <div id="cal-month-year" class="cal-title"></div>
                    <button id="cal-next" class="cal-nav" aria-label="Next month">›</button>
                </div>
                <div id="cal-grid" class="cal-grid"></div>
                <div id="cal-day-appointments" class="cal-day-appointments"><em>Select a day to see appointments</em></div>
            </div>
        `;
    }

    function attachAppointmentsCalendar(apptsByDate, prefsByAddressString, options = {}) {
        try {
            const pad = (n) => n.toString().padStart(2, '0');

            const today = new Date();
            let viewYear = today.getFullYear();
            let viewMonth = today.getMonth();

            function renderCalendar(year, month) {
                const monthStart = new Date(year, month, 1);
                const monthName = monthStart.toLocaleString(undefined, { month: 'long' });
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                const startWeekday = monthStart.getDay();

                const grid = document.getElementById('cal-grid');
                const title = document.getElementById('cal-month-year');
                if (!grid || !title) return;
                title.textContent = `${monthName} ${year}`;

                const weekdays = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
                let html = '';
                weekdays.forEach(w => { html += `<div class="cal-weekday">${w}</div>`; });

                for (let i = 0; i < startWeekday; i++) {
                    html += `<div class="cal-day disabled"></div>`;
                }

                for (let day = 1; day <= daysInMonth; day++) {
                    const dateStr = `${year}-${pad(month + 1)}-${pad(day)}`;
                    const has = Array.isArray(apptsByDate[dateStr]) && apptsByDate[dateStr].length > 0;
                    const isToday = (new Date().toISOString().slice(0,10) === dateStr);
                    html += `
                        <div class="cal-day ${has? 'has-appt':''} ${isToday? 'today':''}" data-date="${dateStr}">
                            <div class="date-num">${day}</div>
                            ${has? '<div class="dot" aria-hidden="true"></div>' : ''}
                        </div>
                    `;
                }

                grid.innerHTML = html;

                    // Attach click listeners to all in-month days so every day is clickable
                    grid.querySelectorAll('.cal-day').forEach(el => {
                        if (el.classList.contains('disabled')) return; // skip leading/trailing empty cells
                        // ensure no visual fading class is enforced here; keep days equally clickable
                        el.addEventListener('click', () => {
                            // clear previous selection
                            grid.querySelectorAll('.cal-day.selected').forEach(s => s.classList.remove('selected'));
                            el.classList.add('selected');
                            const ds = el.getAttribute('data-date');
                            // Always render the details pane for the clicked date (even if empty)
                            showAppointmentsForDate(ds);
                            const details = document.getElementById('cal-day-appointments');
                            if (details && typeof details.scrollIntoView === 'function') {
                                try { details.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch(e) { details.scrollIntoView(); }
                            }
                            // call optional callback with the list of appts for this day
                            if (typeof options.onDayClick === 'function') {
                                try { options.onDayClick(ds, apptsByDate[ds] || []); } catch(e) { console.error(e); }
                            }
                        });
                    });
            }

            function showAppointmentsForDate(dateStr) {
                const container = document.getElementById('cal-day-appointments');
                const list = apptsByDate[dateStr] || [];
                if (!container) return;
                let html = `<h4>Appointments on ${dateStr}</h4>`;
                html += '<div class="appt-list">';
                if (list.length === 0) {
                    html += `<div class="no-appts">No appointments on ${dateStr}.</div>`;
                }
                list.forEach(a => {
                    const prefs = prefsByAddressString[a.address] || null;
                    html += `
                        <div class="appt-item" data-appt-id="${a.id || ''}" data-appt-idx="${list.indexOf(a)}">
                            <div class="appt-view">
                                <div><strong>${a.service_names || 'General Cleaning'}</strong> — ${a.time.slice(0,5)}</div>
                                <div class="small">📍 ${a.address}</div>
                                <div class="small">🔗 Source: ${a._source || 'DB'}</div>
                                ${a.notes? `<div class="small">Notes: ${a.notes}</div>` : ''}
                                ${prefs ? `
                                    <div class="small" style="margin-top:0.5rem"><strong>Preferences:</strong></div>
                                    <ul class="small" style="margin:0.25rem 0 0 1rem; padding:0; list-style:disc;">
                                        <li>Allergies: ${prefs.allergies || 'None specified'}</li>
                                        <li>Pets: ${prefs.pets || 'None specified'}</li>
                                        <li>Kids: ${prefs.kids || 'None specified'}</li>
                                        <li>Size: ${prefs.square_footage ? prefs.square_footage + ' m²' : 'Not specified'}</li>
                                        <li>Notes: ${prefs.preference_notes || 'None'}</li>
                                    </ul>
                                ` : ''}
                            </div>
                            ${options.editable ? '<div class="appt-actions"><button class="appt-edit">Edit</button></div>' : ''}
                        </div>
                    `;
                });
                html += '</div>';
                // --- Append create-new form (when editable) ---
                if (options.editable) {
                    // build address options if provided
                    let addrOptions = '<option value="">-- Select address --</option>';
                    if (Array.isArray(options.addresses)) {
                        options.addresses.forEach(addr => {
                            const label = `${addr.street_and_number}, ${addr.postal_code} ${addr.city_name}`;
                            addrOptions += `<option value="${addr.id}">${label}</option>`;
                        });
                    }
                    const safeDate = dateStr.replace(/[^0-9]/g, '');
                    html += `
                        <div class="appt-create" id="appt-create-${safeDate}">
                            <h5>Create appointment on ${dateStr}</h5>
                            <div class="appt-create-form">
                                <label>Date: <input type="date" name="date" value="${dateStr}"></label>
                                <label>Time: <input type="time" name="time" value="09:00"></label>
                                <label>Address: <select name="address_id">${addrOptions}</select></label>
                                <div class="service-checkboxes">
                                    <label>Services:</label>
                                    <div class="service-options">
                                        <label><input type="checkbox" name="service_names" value="Deep Clean"> Deep Clean</label>
                                        <label><input type="checkbox" name="service_names" value="Bathroom"> Bathroom</label>
                                        <label><input type="checkbox" name="service_names" value="Kitchen Full"> Kitchen Full</label>
                                        <label><input type="checkbox" name="service_names" value="Basement"> Basement</label>
                                        <label><input type="checkbox" name="service_names" value="Dust Removal"> Dust Removal</label>
                                        <label><input type="checkbox" name="service_names" value="Quick Tidy-Up"> Quick Tidy-Up</label>
                                        <label><input type="checkbox" name="service_names" value="Windows Inside & Out"> Windows Inside & Out</label>
                                        <label><input type="checkbox" name="service_names" value="Living Room Detail"> Living Room Detail</label>
                                        <label><input type="checkbox" name="service_names" value="Fridge Cleaning"> Fridge Cleaning</label>
                                        <label><input type="checkbox" name="service_names" value="Move-In Cleaning"> Move-In Cleaning</label>
                                        <label><input type="checkbox" name="service_names" value="Spring Cleaning"> Spring Cleaning</label>
                                        <label><input type="checkbox" name="service_names" value="Post-Party Cleanup"> Post-Party Cleanup</label>
                                        <label><input type="checkbox" name="service_names" value="Surface Sanitatization"> Surface Sanitatization</label>
                                        <label><input type="checkbox" name="service_names" value="Full House Deep Cleanup"> Full House Deep Cleanup</label>
                                        <label><input type="checkbox" name="service_names" value="Pet Hair Removal"> Pet Hair Removal</label>
                                        <label><input type="checkbox" name="service_names" value="End Of Lease Cleaning"> End Of Lease Cleaning</label>
                                        <label><input type="checkbox" name="service_names" value="Trash & Recycling"> Trash & Recycling</label>
                                        <label><input type="checkbox" name="service_names" value="Closet Organization"> Closet Organization</label>
                                        <label><input type="checkbox" name="service_names" value="Renovation Cleanup"> Renovation Cleanup</label>
                                        <label><input type="checkbox" name="service_names" value="Garage Cleaning"> Garage Cleaning</label>
                                    </div>
                                </div>
                                <label>Notes: <input type="text" name="notes" placeholder="Optional notes"></label>
                                <div class="create-actions">
                                    <button class="create-save">Create</button>
                                </div>
                            </div>
                        </div>
                    `;
                }
                container.innerHTML = html;
                // attach click handlers to appt items to allow callbacks (e.g., reschedule)
                    if (typeof options.onAppointmentClick === 'function') {
                        container.querySelectorAll('.appt-item').forEach((el, idx) => {
                            el.addEventListener('click', (e) => {
                                // avoid firing when clicking edit buttons
                                if (e.target && e.target.classList && e.target.classList.contains('appt-edit')) return;
                                const appt = list[idx];
                                try { options.onAppointmentClick(appt); } catch(e) { console.error(e); }
                            });
                        });
                    }

                    // Inline edit handlers (manual mode) -> call options.onAppointmentUpdate
                    if (options.editable) {
                        container.querySelectorAll('.appt-item').forEach((el, idx) => {
                            const editBtn = el.querySelector('.appt-edit');
                            if (!editBtn) return;
                            editBtn.addEventListener('click', (ev) => {
                                ev.stopPropagation();
                                const appt = list[idx];
                                // build inline edit form
                                // Build address select HTML if addresses were provided in options
                                let addressSelectHtml = '';
                                if (Array.isArray(options.addresses) && options.addresses.length > 0) {
                                    addressSelectHtml = '<label>Address: <select name="address_id">';
                                    options.addresses.forEach(addr => {
                                        const label = `${addr.street_and_number}, ${addr.postal_code} ${addr.city_name}`;
                                        const selected = (addr.id == appt.address_id) ? ' selected' : '';
                                        addressSelectHtml += `<option value="${addr.id}"${selected}>${label}</option>`;
                                    });
                                    addressSelectHtml += '</select></label>';
                                }

                                const formHtml = `
                                    <div class="appt-edit-form">
                                        <label>Date: <input type="date" name="date" value="${appt.date}"></label>
                                        <label>Time: <input type="time" name="time" value="${appt.time.slice(0,5)}"></label>
                                        ${addressSelectHtml}
                                        <div class="service-checkboxes">
                                            <label>Services:</label>
                                            <div class="service-options-edit">
                                                <!-- service checkboxes will be injected here -->
                                            </div>
                                        </div>
                                        <label>Notes: <input type="text" name="notes" value="${(appt.notes||'').replace(/"/g,'&quot;')}"></label>
                                        <div class="edit-actions">
                                            <button class="save-edit">Save</button>
                                            <button class="cancel-edit">Cancel</button>
                                        </div>
                                    </div>
                                `;
                                const viewEl = el.querySelector('.appt-view');
                                viewEl.style.display = 'none';
                                const actionsEl = el.querySelector('.appt-actions');
                                if (actionsEl) actionsEl.style.display = 'none';
                                const wrapper = document.createElement('div');
                                wrapper.className = 'appt-edit-wrapper';
                                wrapper.innerHTML = formHtml;
                                el.appendChild(wrapper);

                                // populate the service checkboxes in the edit form based on existing appt services
                                (function populateEditServices(){
                                    const serviceOptions = [
                                        'Deep Clean','Bathroom','Kitchen Full','Basement','Dust Removal','Quick Tidy-Up',
                                        'Windows Inside & Out','Living Room Detail','Fridge Cleaning','Move-In Cleaning','Spring Cleaning',
                                        'Post-Party Cleanup','Surface Sanitatization','Full House Deep Cleanup','Pet Hair Removal',
                                        'End Of Lease Cleaning','Trash & Recycling','Closet Organization','Renovation Cleanup','Garage Cleaning'
                                    ];
                                    const existing = (appt.service_names || '').split(',').map(s => s.trim().toLowerCase());
                                    const svcContainer = wrapper.querySelector('.service-options-edit');
                                    if (!svcContainer) return;
                                    svcContainer.innerHTML = serviceOptions.map(s => {
                                        const safe = s.replace(/"/g,'&quot;');
                                        const checked = existing.includes(s.toLowerCase()) ? ' checked' : '';
                                        return `<label><input type="checkbox" name="service_names" value="${safe}"${checked}> ${s}</label>`;
                                    }).join('');
                                })();

                                const saveBtn = wrapper.querySelector('.save-edit');
                                const cancelBtn = wrapper.querySelector('.cancel-edit');
                                saveBtn.addEventListener('click', async (e) => {
                                    e.preventDefault();
                                    const dateVal = wrapper.querySelector('input[name="date"]').value;
                                    const timeVal = wrapper.querySelector('input[name="time"]').value;
                                    // collect selected services from checkboxes
                                    const selectedServices = Array.from(wrapper.querySelectorAll('input[name="service_names"]:checked')).map(i=>i.value.trim());
                                    const serviceVal = selectedServices.join(', ');
                                    const notesVal = wrapper.querySelector('input[name="notes"]').value;
                                    const addrEl = wrapper.querySelector('select[name="address_id"]');
                                    const addressIdVal = addrEl ? addrEl.value : (appt.address_id || null);
                                    const updated = { date: dateVal, time: timeVal, address_id: addressIdVal, service_names: serviceVal, notes: notesVal };
                                    if (typeof options.onAppointmentUpdate === 'function') {
                                        try { await options.onAppointmentUpdate(appt, updated); } catch(err) { console.error(err); }
                                    }
                                    // remove edit UI after update (the caller may refresh the calendar)
                                    wrapper.remove();
                                    if (viewEl) viewEl.style.display = '';
                                    if (actionsEl) actionsEl.style.display = '';
                                });
                                cancelBtn.addEventListener('click', (e) => {
                                    e.preventDefault();
                                    // remove edit wrapper and show view again
                                    wrapper.remove();
                                    if (viewEl) viewEl.style.display = '';
                                    if (actionsEl) actionsEl.style.display = '';
                                });
                            });
                        });
                        // attach create handler
                        const createWrapper = container.querySelector('.appt-create');
                        if (createWrapper) {
                            const saveBtn = createWrapper.querySelector('.create-save');
                            saveBtn.addEventListener('click', async (ev) => {
                                ev.preventDefault();
                                const form = createWrapper.querySelector('.appt-create-form');
                                const dateVal = form.querySelector('input[name="date"]').value;
                                const timeVal = form.querySelector('input[name="time"]').value;
                                const addrEl = form.querySelector('select[name="address_id"]');
                                const addressId = addrEl ? addrEl.value : '';
                                const selectedServices = Array.from(form.querySelectorAll('input[name="service_names"]:checked')).map(i=>i.value.trim());
                                const serviceVal = selectedServices.join(', ');
                                const notesVal = form.querySelector('input[name="notes"]').value;
                                const payload = { date: dateVal, time: timeVal, address_id: addressId, service_names: serviceVal, notes: notesVal };
                                if (typeof options.onCreateAppointment === 'function') {
                                    try {
                                        await options.onCreateAppointment(payload);
                                    } catch (e) { console.error('onCreateAppointment failed', e); }
                                }
                            });
                        }
                    }
            }

            // Navigation handlers
            const prevBtn = document.getElementById('cal-prev');
            const nextBtn = document.getElementById('cal-next');
            if (prevBtn) prevBtn.addEventListener('click', () => {
                viewMonth -= 1;
                if (viewMonth < 0) { viewMonth = 11; viewYear -= 1; }
                renderCalendar(viewYear, viewMonth);
                const details = document.getElementById('cal-day-appointments');
                if (details) details.innerHTML = '<em>Select a day to see appointments</em>';
                const modalBody = document.getElementById('modal-body');
                if (modalBody) { try { modalBody.scrollTo({ top: 0, behavior: 'smooth' }); } catch(e) { modalBody.scrollTop = 0; } }
            });
            if (nextBtn) nextBtn.addEventListener('click', () => {
                viewMonth += 1;
                if (viewMonth > 11) { viewMonth = 0; viewYear += 1; }
                renderCalendar(viewYear, viewMonth);
                const details = document.getElementById('cal-day-appointments');
                if (details) details.innerHTML = '<em>Select a day to see appointments</em>';
                const modalBody = document.getElementById('modal-body');
                if (modalBody) { try { modalBody.scrollTo({ top: 0, behavior: 'smooth' }); } catch(e) { modalBody.scrollTop = 0; } }
            });

            // Initial render & auto-select
            renderCalendar(viewYear, viewMonth);
            const todayStr = new Date().toISOString().slice(0,10);
            if (apptsByDate[todayStr]) {
                const todayEl = document.querySelector(`.cal-day[data-date="${todayStr}"]`);
                if (todayEl) { todayEl.classList.add('selected'); showAppointmentsForDate(todayStr); const details = document.getElementById('cal-day-appointments'); if (details && typeof details.scrollIntoView === 'function') { try { details.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch(e) { details.scrollIntoView(); } } }
            }

        } catch (err) {
            console.error('Calendar widget error:', err);
        }
    }

    window.getCalendarSkeleton = getCalendarSkeleton;
    window.attachAppointmentsCalendar = attachAppointmentsCalendar;
})(window);
