// Itinerary reader for Amex GBT (Government of Canada Travel Services) itineraries.
// Text lines in, travel segments out. Pure functions: no network, no storage, no page access,
// so it can be tested on its own (test_itin.py runs it in Node). Inlined into app.html by build.py.
const ITIN = (() => {
  const fold = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const pad = n => String(n).padStart(2, '0');
  const MON = { jan: 1, january: 1, janv: 1, janvier: 1, feb: 2, february: 2, fev: 2, fevr: 2, fevrier: 2, mar: 3, march: 3, mars: 3, apr: 4, april: 4, avr: 4, avril: 4,
    may: 5, mai: 5, jun: 6, june: 6, juin: 6, jul: 7, july: 7, juil: 7, juill: 7, juillet: 7, aug: 8, august: 8, aou: 8, aout: 8, sep: 9, sept: 9, september: 9, septembre: 9,
    oct: 10, october: 10, octobre: 10, nov: 11, november: 11, novembre: 11, dec: 12, december: 12, decembre: 12 };
  // Airports used when only a three-letter code is known (the summary table). Canadian airports and wings.
  const AIRPORTS = { YWG: 'Winnipeg', YOW: 'Ottawa', YYZ: 'Toronto', YTZ: 'Toronto', YUL: 'Montréal', YVR: 'Vancouver', YYC: 'Calgary', YEG: 'Edmonton', YHZ: 'Halifax',
    YQB: 'Québec', YQM: 'Moncton', YFC: 'Fredericton', YSJ: 'Saint John', YYT: "St. John's", YXE: 'Saskatoon', YQR: 'Regina', YXU: 'London', YKF: 'Kitchener', YHM: 'Hamilton',
    YQT: 'Thunder Bay', YXY: 'Whitehorse', YZF: 'Yellowknife', YFB: 'Iqaluit', YYG: 'Charlottetown', YQY: 'Sydney', YGK: 'Kingston', YTR: 'Trenton', YOD: 'Cold Lake',
    YQQ: 'Comox', YYR: 'Goose Bay', YBG: 'Bagotville', YQX: 'Gander', YXX: 'Abbotsford', YYJ: 'Victoria', YLW: 'Kelowna', YXS: 'Prince George', YQU: 'Grande Prairie',
    YMM: 'Fort McMurray', YZX: 'Greenwood', YSB: 'Sudbury', YAM: 'Sault Ste. Marie', YTS: 'Timmins', YQG: 'Windsor', YBR: 'Brandon', YQL: 'Lethbridge', YXH: 'Medicine Hat',
    YKA: 'Kamloops', YCD: 'Nanaimo', YXT: 'Terrace', YPR: 'Prince Rupert', YQF: 'Red Deer', YXJ: 'Fort St. John', YWK: 'Wabush', YDF: 'Deer Lake', YZV: 'Sept-Îles',
    YBC: 'Baie-Comeau', YVO: "Val-d'Or", YUY: 'Rouyn-Noranda', YGR: 'Îles-de-la-Madeleine', YSM: 'Fort Smith', YEV: 'Inuvik', YCB: 'Cambridge Bay', YRB: 'Resolute' };

  // "15 October 2026, 11:40", "15 oct. 2026 11 h 40", "October 15, 2026 11:40 AM", "2026-10-15T11:40"
  function when(v) {
    const s = fold(v).replace(/\s+/g, ' ');
    let d = '', m = s.match(/(\d{4})-(\d{2})-(\d{2})/), rest = s;
    if (m) d = `${m[1]}-${m[2]}-${m[3]}`;
    else if ((m = s.match(/\b(\d{1,2})(?:er)? ([a-z]{3,9})\.?,? (\d{4})/)) && MON[m[2]]) d = `${m[3]}-${pad(MON[m[2]])}-${pad(m[1])}`;
    else if ((m = s.match(/\b([a-z]{3,9})\.? (\d{1,2}),? (\d{4})/)) && MON[m[1]]) d = `${m[3]}-${pad(MON[m[1]])}-${pad(m[2])}`;
    else m = null;
    if (m) rest = s.slice(0, m.index) + ' ' + s.slice(m.index + m[0].length);
    let t = ''; const tm = rest.match(/\b(\d{1,2}) ?(?::|h) ?(\d{2})\b ?(a\.?m\.?|p\.?m\.?)?/);
    if (tm) { let h = +tm[1]; const ap = tm[3] && tm[3][0]; if (ap === 'p' && h < 12) h += 12; if (ap === 'a' && h === 12) h = 0; if (h < 24 && +tm[2] < 60) t = pad(h) + tm[2]; }
    return { date: d, time: t };
  }
  const NOTCITY = /^(canada|united states( of america)?|usa|u\.?s\.?a?\.?|etats-unis|[a-z]{2}|([a-z]{2} )?[a-z]\d[a-z] ?\d[a-z]\d|([a-z]{2} )?\d{5}(-\d{4})?)$/;
  // "Winnipeg James Armstrong Richardson Intl Airport, Winnipeg, Canada (YWG)" -> name, city, code
  function place(v) {
    let s = String(v || '').replace(/\s+/g, ' ').trim(), code = '';
    const m = s.match(/\(([A-Z]{3,4})\)\s*$/); if (m) { code = m[1]; s = s.slice(0, m.index).trim(); }
    const parts = s.split(',').map(x => x.trim()).filter(Boolean);
    while (parts.length > 1 && NOTCITY.test(fold(parts[parts.length - 1]))) parts.pop();
    let city = parts.length > 1 ? parts[parts.length - 1] : (AIRPORTS[code] || parts[0] || code);
    if (AIRPORTS[code] && fold(AIRPORTS[code]) === fold(city)) city = AIRPORTS[code]; // keep the accents
    return { name: parts[0] || code, city, code };
  }
  // a value that is only a date and time, with no place in it
  const onlyWhen = v => !!when(v).date && !/[a-z]{3,}/.test(fold(v)
    .replace(/\d{4}-\d{2}-\d{2}(t\d{2}:\d{2})?/, '').replace(/\b\d{1,2}(er)? [a-z]{3,9}\.?,? \d{4}/, '').replace(/\b[a-z]{3,9}\.? \d{1,2},? \d{4}/, '')
    .replace(/\d{1,2} ?(:|h) ?\d{2} ?(a\.?m\.?|p\.?m\.?)?/, '').replace(/\b(mon|tue|wed|thu|fri|sat|sun|lun|mar|mer|jeu|ven|sam|dim)[a-z]*\.?/g, '').replace(/\b(at|a)\b/g, ''));
  const isPort = p => /\b(airport|aeroport|intl|international|aerogare)\b/.test(fold(p.name));
  const isStation = p => /\b(station|gare|terminal|via)\b/.test(fold(p.name));
  const amt = v => parseFloat(String(v).replace(/[\s,](?=\d{3}\b)/g, '').replace(',', '.'));

  const RX = {
    dep: /^(?:departing|departure|depart|départ)\s*:\s*(.*)$/i,
    arr: /^(?:arriving|arrival|arrive|arrivée)\s*:\s*(.*)$/i,
    when: /^(?:date\s*\/\s*time|date and time|date\s*\/\s*heure|date et heure|date)\s*:\s*(.*)$/i,
    pick: /^(?:pick[- ]?up(?: location| date(?:\s*\/\s*time)?)?|prise en charge|cueillette)\s*:\s*(.*)$/i,
    drop: /^(?:drop[- ]?off(?: location| date(?:\s*\/\s*time)?)?|return(?: location| date(?:\s*\/\s*time)?)|retour|remise)\s*:\s*(.*)$/i,
    cin: /^(?:check[- ]?in(?: date)?|date d'arrivée)\s*:\s*(.*)$/i,
    cout: /^(?:check[- ]?out(?: date)?|date de départ)\s*:\s*(.*)$/i,
    addr: /^(?:address|adresse)\s*:\s*(.*)$/i,
    hotel: /^(?:hotel|hôtel|property|établissement)(?: name| nom)?\s*:\s*(.*)$/i,
    ticket: /^(?:ticket number|numéro de billet)\s*:\s*(\S+)/i,
    fare: /^(?:ticket amount|montant du billet)\s*:\s*([\d][\d\s.,]*)\s*([A-Z]{3})\b/i,
    total: /^(?:total amount|montant total)\s*:\s*([\d][\d\s.,]*)\s*([A-Z]{3})\b/i,
    fee: /^(?:fee|frais)\s*(\d+)\s*total\s*:\s*([\d][\d\s.,]*)\s*([A-Z]{3})\b/i,
    flight: /\b(?:flight|vol)\s*(?:n[o°]\.?\s*)?#?\s*:?\s*([A-Z0-9]{2})\s?(\d{1,4})\b/i,
    rail: /\b(?:train|rail|via rail|amtrak)\b/i,
    railNo: /\btrain\s*(?:n[o°]\.?\s*)?#?\s*:?\s*(\d{1,5})\b/i,
    bus: /\b(?:bus|coach|motorcoach|autocar|autobus)\b/i,
    car: /\b(?:car rental|rental car|location de (?:voiture|véhicule)|enterprise|national car|avis|hertz|budget|alamo|thrifty|dollar rent)\b/i,
    label: /^[^:]{1,40}\s:|^[^:]{1,40}:/,
    sum: /^(\d{1,2} [a-zéû]{3,9}\.? \d{4}) ([A-Z]{3}) ?- ?([A-Z]{3}) ([A-Z0-9]{2} ?\d{1,4}) (\d{1,2}:\d{2}) ?- ?(\d{1,2}:\d{2})/i,
  };

  // "Traveller: | Mr THOMAS SAMPLE | DOE | Travel Directive Module : | ..." -> given and surname, in normal case.
  // The itinerary puts given names and surname in separate cells (" | " between them). Without cells
  // (pasted text), the capitalised words before the next label are the name and the last one is the surname.
  const TITLE = /^(?:mr|mrs|ms|miss|mx|dr|m|mme|mlle)\.?$/i;
  const nameCase = v => v.toLowerCase().replace(/(^|[\s'’-])(\p{L})/gu, (_, a, b) => a + b.toUpperCase());
  function traveller(lines) {
    for (const raw of lines) {
      const m = String(raw).replace(/\t/g, ' | ').replace(/[\u00a0\s]+/g, ' ').trim().match(/^(?:traveller|traveler|voyageur|voyageuse)\s*:\s*(.*)$/i); if (!m) continue;
      let cells = m[1].split('|').map(x => x.trim()).filter(Boolean);
      const stop = cells.findIndex(c => c.includes(':')); if (stop >= 0) cells = cells.slice(0, stop);
      const words = c => c.split(' ').filter(w => !TITLE.test(w));
      let given, surname;
      if (cells.length >= 2) { given = words(cells[0]).join(' '); surname = cells[1]; }
      else {
        const caps = []; for (const w of words(m[1].split(':')[0].replace(/\|/g, ' ').replace(/\s+/g, ' ').trim())) { if (/^[\p{Lu}'’-]+$/u.test(w)) caps.push(w); else break; }
        if (caps.length < 2) continue; surname = caps.pop(); given = caps.join(' ');
      }
      if (given && surname) return { given: nameCase(given), surname: nameCase(surname) };
    }
    return null;
  }

  // lines: the document text, one visual line per entry
  function parse(lines) {
    const L = lines.map(l => String(l).replace(/\s*\|\s*/g, ' ').replace(/[ \s]+/g, ' ').trim()).filter(Boolean);
    const segs = [], hotels = [], fares = {}, fees = {}, totals = new Set(), summary = [], locator = [], tan = [];
    let kind = '', num = '', carrier = '', seg = null, side = '', hotel = null, ticket = '', addr = null;
    const head = []; // recent short lines that are not labels: carrier, hotel name
    const val = (m, i) => { if (m[1] && m[1].trim()) return [m[1].trim(), i]; const n = L[i + 1]; return n && !RX.label.test(n) ? [n, i + 1] : ['', i]; };
    const done = s => {
      if (!s || !s.from || !s.to || !s.dep || !s.dep.date) return;
      if (s.kind !== 'car') {
        if (isPort(s.from) || isPort(s.to)) s.kind = 'air';
        else if (s.kind === 'air' && !(s.from.code && s.to.code)) s.kind = isStation(s.from) ? 'rail' : '';
        else if (!s.kind && isStation(s.from)) s.kind = 'rail';
      }
      if (!s.arr) s.arr = { date: '', time: '' };
      const k = [s.kind, s.from.code || fold(s.from.city), s.dep.date, s.dep.time].join('|');
      if (!segs.some(x => x.k === k)) { s.k = k; segs.push(s); }
    };
    for (let i = 0; i < L.length; i++) {
      const l = L[i]; let m, v;
      if ((m = l.match(/^(?:trip locator|localisateur(?: du voyage)?|record locator)\s*:?\s*([A-Z0-9]{6})\b/i))) locator.push(m[1].toUpperCase());
      if ((m = l.match(/^TAN\s*:\s*([A-Z0-9][A-Z0-9-]{3,})\b/))) tan.push(m[1]);
      if ((m = l.match(RX.sum))) { const w = when(m[1]); summary.push({ date: w.date, from: m[2], to: m[3], num: m[4].replace(' ', ''), dep: m[5].replace(':', '').padStart(4, '0'), arr: m[6].replace(':', '').padStart(4, '0') }); continue; }
      if ((m = l.match(RX.ticket))) { ticket = m[1]; continue; }
      if ((m = l.match(RX.fare))) { fares[ticket || ('t' + i)] = { n: amt(m[1]), cur: m[2].toUpperCase() }; continue; }
      if ((m = l.match(RX.total))) { totals.add(amt(m[1]) + ' ' + m[2].toUpperCase()); continue; }
      if ((m = l.match(RX.fee))) { fees[m[1]] = { n: amt(m[2]), cur: m[3].toUpperCase() }; continue; }
      if ((m = l.match(RX.dep))) { [v, i] = val(m, i); done(seg); seg = { kind, num, carrier, from: place(v), to: null, dep: null, arr: null }; side = 'dep'; continue; }
      if ((m = l.match(RX.arr)) && seg) { [v, i] = val(m, i); seg.to = place(v); side = 'arr'; continue; }
      if ((m = l.match(RX.pick))) {
        [v, i] = val(m, i); done(seg); const w = when(v);
        seg = { kind: 'car', num: '', carrier: kind === 'car' ? carrier : '', from: null, to: null, dep: null, arr: null };
        if (onlyWhen(v)) seg.dep = w; else seg.from = place(v);
        side = 'dep'; continue;
      }
      if ((m = l.match(RX.drop)) && seg && seg.kind === 'car') {
        [v, i] = val(m, i); const w = when(v);
        if (onlyWhen(v)) { seg.arr = w; if (!seg.to) seg.to = seg.from; } else seg.to = place(v);
        side = 'arr'; if (seg.arr && seg.to) { done(seg); seg = null; side = ''; } continue;
      }
      if ((m = l.match(RX.hotel))) { [v, i] = val(m, i); hotel = { name: v, city: '', in: '', out: '' }; continue; }
      if ((m = l.match(RX.addr))) { [v, i] = val(m, i); addr = { v, i }; if (hotel && !hotel.city) hotel.city = place(v).city; else { const h = hotels[hotels.length - 1]; if (h && !h.city && i - h.i < 12) h.city = place(v).city; } continue; }
      if ((m = l.match(RX.cin))) {
        [v, i] = val(m, i); done(seg); seg = null; side = '';
        if (!hotel || hotel.out) hotel = { name: head.length ? head[head.length - 1] : '', city: '', in: '', out: '' };
        if (!hotel.city && addr && i - addr.i < 12) hotel.city = place(addr.v).city;
        hotel.in = when(v).date; continue;
      }
      if ((m = l.match(RX.cout)) && hotel) {
        [v, i] = val(m, i); hotel.out = when(v).date; hotel.i = i;
        if (hotel.in && hotel.out) hotels.push(hotel);
        continue;
      }
      if ((m = l.match(RX.when))) {
        [v, i] = val(m, i); const w = when(v);
        if (seg && side === 'dep' && !seg.dep) { seg.dep = w; continue; }
        if (seg && side === 'arr' && !seg.arr) { seg.arr = w; if (!seg.to) seg.to = seg.from; done(seg); seg = null; side = ''; continue; }
        continue;
      }
      if ((m = l.match(/\b(?:location|lieu|office|comptoir)\s*:\s*(.*)$/i)) && seg && seg.kind === 'car') { const p = place(m[1]); if (side === 'arr') seg.to = p; else if (!seg.from) seg.from = p; continue; }
      // segment headers set the kind for the next Departing line
      if (l.length <= 70) {
        if ((m = l.match(RX.flight))) { kind = 'air'; num = (m[1] + m[2]).toUpperCase(); carrier = head.length ? head[head.length - 1] : ''; }
        else if (RX.car.test(l)) { if (kind !== 'car' || !carrier) carrier = l.replace(/\s*\b(?:confirmation|booking reference|status)\b.*$/i, ''); kind = 'car'; num = ''; }
        else if (RX.rail.test(l) && !/\b(?:please|must|should|veuillez)\b/i.test(l)) { kind = 'rail'; num = (l.match(RX.railNo) || [])[1] || ''; carrier = l; }
        else if (RX.bus.test(l) && !/\b(?:please|must|should|veuillez)\b/i.test(l)) { kind = 'bus'; num = ''; carrier = l; }
        if (!RX.label.test(l)) { head.push(l); if (head.length > 4) head.shift(); }
      }
    }
    done(seg);
    // Summary table only: flights with codes and times, no detail blocks
    summary.forEach(r => {
      if (!r.date || segs.some(s => s.dep.date === r.date && (s.num === r.num || s.dep.time === r.dep))) return;
      const P = c => ({ name: AIRPORTS[c] ? AIRPORTS[c] + ' airport' : c, city: AIRPORTS[c] || c, code: c });
      const arrDate = r.arr < r.dep ? new Date(Date.parse(r.date + 'T00:00:00Z') + 864e5).toISOString().slice(0, 10) : r.date;
      segs.push({ kind: 'air', num: r.num, carrier: '', from: P(r.from), to: P(r.to), dep: { date: r.date, time: r.dep }, arr: { date: arrDate, time: r.arr }, k: 'sum' + r.num + r.date });
    });
    segs.sort((a, b) => (a.dep.date + a.dep.time).localeCompare(b.dep.date + b.dep.time));
    // money: one ticket amount per e-ticket plus the agency service fees
    const cur = Object.values(fares).concat(Object.values(fees)).map(x => x.cur)[0] || 'CAD';
    let fare = Object.values(fares).reduce((t, x) => t + (x.cur === cur ? x.n : 0), 0);
    if (!fare && totals.size) fare = [...totals].reduce((t, x) => { const [n, c] = x.split(' '); return t + (c === cur ? +n : 0); }, 0);
    const fee = Object.values(fees).reduce((t, x) => t + (x.cur === cur ? x.n : 0), 0);
    return { segs, hotels, fare: Math.round(fare * 100) / 100, fee: Math.round(fee * 100) / 100, cur, locator: [...new Set(locator)], tan: [...new Set(tan)], traveller: traveller(lines) };
  }

  // Combine what several files found (an outbound and a separate return booking, say)
  function merge(list) {
    const out = { segs: [], hotels: [], fare: 0, fee: 0, cur: 'CAD', locator: [], tan: [], traveller: null };
    list.forEach(f => {
      f.segs.forEach(s => { if (!out.segs.some(x => x.k === s.k)) out.segs.push(s); });
      f.hotels.forEach(h => { if (!out.hotels.some(x => x.in === h.in && fold(x.name) === fold(h.name))) out.hotels.push(h); });
      if (f.fare || f.fee) { if (!out.fare && !out.fee) out.cur = f.cur; if (f.cur === out.cur) { out.fare += f.fare; out.fee += f.fee; } }
      f.locator.forEach(x => out.locator.includes(x) || out.locator.push(x));
      (f.tan || []).forEach(x => out.tan.includes(x) || out.tan.push(x));
      if (!out.traveller && f.traveller) out.traveller = f.traveller;
    });
    out.segs.sort((a, b) => (a.dep.date + a.dep.time).localeCompare(b.dep.date + b.dep.time));
    out.fare = Math.round(out.fare * 100) / 100; out.fee = Math.round(out.fee * 100) / 100;
    return out;
  }

  const sameCity = (a, b) => !!(a && b && fold(a.city) && fold(a.city) === fold(b.city));
  const roundTrip = f => f.segs.length > 1 && sameCity(f.segs[0].from, f.segs[f.segs.length - 1].to);
  const E = () => ({ date: '', time: '' });
  const mins = (a, b) => (Date.parse(b.date + 'T' + b.time.slice(0, 2) + ':' + b.time.slice(2) + 'Z') - Date.parse(a.date + 'T' + a.time.slice(0, 2) + ':' + a.time.slice(2) + 'Z')) / 6e4;

  // Turn segments into the stops of section B. Each stop: where, arrival, departure, and how the
  // member leaves it. Legs the itinerary does not cover (home to the airport) keep an empty mode.
  function plan(f, o = {}) {
    const moves = f.segs.filter(s => s.kind !== 'car' || !sameCity(s.from, s.to));
    const cars = f.segs.filter(s => s.kind === 'car' && sameCity(s.from, s.to));
    const P = (p, kind) => ({ p, kind, arr: E(), dep: E(), mode: '' });
    const st = [];
    moves.forEach(s => {
      const last = st[st.length - 1];
      if (last && sameCity(last.p, s.from)) {
        if (!last.dep.date) { last.dep = s.dep; last.mode = s.kind; if (s.from.code !== last.p.code) last.p = Object.assign({}, last.p, { code: '' }); }
      } else {
        const p = P(s.from, s.kind); p.dep = s.dep; p.mode = s.kind; st.push(p);
      }
      const q = P(s.to, s.kind); q.arr = s.arr; st.push(q);
    });
    (f.hotels || []).slice().sort((a, b) => a.in.localeCompare(b.in)).forEach(h => {
      if (!h.city || !h.in) return;
      const hp = { name: h.name, city: h.city, code: '' };
      let k = -1; st.forEach((s, i) => { const a = s.arr.date || s.dep.date; if (a && a <= h.in) k = i; });
      if (k < 0 || sameCity(st[k].p, hp)) return;
      const s = st[k], H = P(hp, 'hotel'); H.arr = { date: h.in, time: '' }; H.dep = { date: h.out || '', time: '' };
      if (s.dep.date && s.dep.date >= (h.out || h.in)) {
        const back = P(s.p, s.kind); back.arr = { date: h.out || '', time: '' }; back.dep = s.dep; back.mode = s.mode;
        s.dep = { date: h.in, time: '' }; s.mode = '';
        st.splice(k + 1, 0, H, back);
      } else if (!s.dep.date) {
        s.dep = { date: h.in, time: '' }; s.mode = '';
        if (st[k + 1]) H.mode = ''; else H.dep = E();
        st.splice(k + 1, 0, H);
      }
    });
    // A rental car picked up and returned in the same city covers the legs with no booked transport
    // (compared by date, and by time too when both sides have one)
    const le = (x, y) => x.date < y.date || (x.date === y.date && (!x.time || !y.time || x.time <= y.time));
    cars.forEach(c => {
      for (let i = 0; i < st.length - 1; i++) {
        const a = st[i], b = st[i + 1];
        if (a.mode || a.kind === 'home' || b.kind === 'home') continue;
        const aAt = a.arr.date ? a.arr : a.dep, bAt = b.arr.date ? b.arr : b.dep;
        if (!aAt.date || !bAt.date || !le(c.dep, a.dep.date ? a.dep : aAt) || !(c.arr.date ? le(bAt, c.arr) : true)) continue;
        a.mode = 'car';
        if (sameCity(a.p, c.from) && a.dep.date === c.dep.date && !a.dep.time) a.dep.time = c.dep.time;
        if (sameCity(b.p, c.to) && b.arr.date === c.arr.date && !b.arr.time) b.arr.time = c.arr.time;
      }
    });
    if (o.residence && st.length) {
      const first = st[0], home = P(null, 'home'); home.dep = { date: first.dep.date, time: '' }; first.arr = { date: first.dep.date, time: '' };
      st.unshift(home);
      const last = st[st.length - 1];
      if (st.length > 2 && sameCity(last.p, st[1].p)) { last.dep = { date: last.arr.date, time: '' }; const h2 = P(null, 'home'); h2.arr = { date: last.arr.date, time: '' }; st.push(h2); }
    }
    const n = st.length;
    return st.map((s, i) => {
      let how = 'city';
      if (s.kind === 'home') how = 'home';
      else if (s.kind !== 'hotel' && s.kind !== 'car' && (i === 0 || (st[i - 1] && st[i - 1].kind === 'home') || (st[i + 1] && st[i + 1].kind === 'home') || (i === n - 1 && n > 2 && sameCity(st[0].p, s.p)))) how = 'port';
      else if (s.kind !== 'hotel' && s.arr.date && s.arr.date === s.dep.date && (s.mode === '' || !s.arr.time || !s.dep.time || mins(s.arr, s.dep) < 360)) how = 'port';
      return { place: s.p, kind: s.kind, how,
        arrDate: i === 0 ? '' : s.arr.date, arrTime: i === 0 ? '' : s.arr.time,
        depDate: i === n - 1 ? '' : s.dep.date, depTime: i === n - 1 ? '' : s.dep.time, mode: i === n - 1 ? '' : s.mode };
    });
  }

  /* ---------- email (.eml) ---------- */
  const bin = s => { const u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i) & 255; return u; };
  const qp = s => s.replace(/=\r?\n/g, '').replace(/=([0-9A-F]{2})/gi, (_, h) => String.fromCharCode(parseInt(h, 16)));
  function words(s) { // =?utf-8?B?...?= in file names
    return String(s || '').replace(/=\?([^?]+)\?([bq])\?([^?]*)\?=/gi, (_, cs, e, t) => {
      try { const b = e.toLowerCase() === 'b' ? bin(atob(t)) : bin(qp(t.replace(/_/g, ' '))); return new TextDecoder(cs).decode(b); } catch (x) { return t; }
    });
  }
  // raw: the file as a binary string (one character per byte). Returns the leaf parts.
  function mime(raw, depth = 0) {
    const cut = raw.search(/\r?\n\r?\n/); if (cut < 0 || depth > 8) return [];
    const hdr = raw.slice(0, cut).replace(/\r?\n[ \t]+/g, ' '), body = raw.slice(cut).replace(/^\r?\n\r?\n/, '');
    const h = k => { const m = hdr.match(new RegExp('^' + k + ':\\s*(.*)$', 'im')); return m ? m[1] : ''; };
    const ct = h('content-type') || 'text/plain', type = ct.split(';')[0].trim().toLowerCase();
    if (type.startsWith('multipart/')) {
      const b = (ct.match(/boundary="?([^";]+)"?/i) || [])[1]; if (!b) return [];
      return body.split('--' + b).slice(1).filter(p => !p.startsWith('--')).flatMap(p => mime(p.replace(/^\r?\n/, ''), depth + 1));
    }
    if (type === 'message/rfc822') return mime(body, depth + 1);
    const enc = h('content-transfer-encoding').trim().toLowerCase();
    let bytes; try { bytes = enc === 'base64' ? bin(atob(body.replace(/[^A-Za-z0-9+/=]/g, ''))) : enc === 'quoted-printable' ? bin(qp(body)) : bin(body); } catch (e) { return []; }
    const name = words((h('content-disposition').match(/filename\*?="?([^";]+)"?/i) || ct.match(/name="?([^";]+)"?/i) || [])[1] || '');
    const charset = ((ct.match(/charset="?([^";\s]+)/i) || [])[1] || 'utf-8').toLowerCase();
    return [{ type, name, bytes, charset }];
  }
  const text = p => { try { return new TextDecoder(p.charset || 'utf-8').decode(p.bytes); } catch (e) { return new TextDecoder('utf-8').decode(p.bytes); } };
  const isPdf = p => p.type === 'application/pdf' || /\.pdf$/i.test(p.name) || (p.bytes.length > 4 && p.bytes[0] === 37 && p.bytes[1] === 80 && p.bytes[2] === 68 && p.bytes[3] === 70);

  return { when, place, parse, merge, plan, roundTrip, mime, text, isPdf, fold, AIRPORTS };
})();
