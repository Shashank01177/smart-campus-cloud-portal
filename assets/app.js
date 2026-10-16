/* ============================================================
   CampusOS – Full-Stack App Layer  (Fixed)
   Connects to Flask + PostgreSQL 18 backend.
   All original design / CSS / animations preserved.
   ============================================================ */

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
let role = "admin", toastTimer, currentUser = null;

/* ── role definitions ── */
const roles = {
  admin: {
    name:"Administrator", initials:"AD", title:"Institution overview",
    sub:"A unified view of the people, learning and services across campus.",
    nav:[["Overview","◫"],["Students","♙"],["Faculty","♧"],["Departments","▦"],
         ["Courses","▤"],["Timetable","▦"],["Hostel","⌂"],["Library","▣"],
         ["Placements","↗"],["Reports","▤"],["SQL Console","⌘"]]
  },
  faculty: {
    name:"Faculty", initials:"FC", title:"Teaching workspace",
    sub:"Your classes, student progress and teaching tasks in one place.",
    nav:[["Overview","◫"],["My courses","▤"],["Timetable","▦"],
         ["Attendance register","☷"],["Enter marks","✎"],["Students","♙"]]
  },
  student: {
    name:"Student", initials:"ST", title:"Your campus journey",
    sub:"Academic progress, classes and campus services at a glance.",
    nav:[["Overview","◫"],["My profile","♙"],["Attendance","◷"],
         ["Marks & transcript","▤"],["Timetable","▦"],["Fee ledger","₹"],
         ["Library","▣"],["Hostel","⌂"],["Placements","↗"]]
  }
};

/* ══════════════════════════════════════════════════════════
   SAFE FETCH  — never throws; always returns {}  on error
   ══════════════════════════════════════════════════════════ */
async function api(url, opts) {
  const res = await fetch(url, opts);
  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    if (!res.ok) throw new Error(`Request failed (${res.status}) for ${url}. The server did not return JSON.`);
    return {};
  }
  const data = await res.json();
  const method = String((opts && opts.method) || "GET").toUpperCase();
  // GET failures must be visible to the page renderer, not silently rendered as empty data.
  if ((!res.ok || data.ok === false) && method === "GET") {
    throw new Error(data.error || `Request failed (${res.status}) for ${url}`);
  }
  return data;
}

/* ══════════════════════════════════════════════════════════
   PAGE SWITCHER
   ══════════════════════════════════════════════════════════ */
function page(v) {
  $("#publicPage").classList.toggle("hidden", v !== "public");
  $("#loginPage").classList.toggle("hidden",  v !== "login");
  $("#dashboard").classList.toggle("hidden",  v !== "dash");
  window.scrollTo({ top:0, behavior:"smooth" });
  if (v === "login") setTimeout(() => $("#email").focus(), 150);
}

$$("[data-login]").forEach(b => b.addEventListener("click", e => { e.preventDefault(); page("login"); }));
$$("[data-home]").forEach(b => b.addEventListener("click",  e => { e.preventDefault(); page("public"); }));
$("#backHome").onclick = () => page("public");

/* Header nav links (#about, #academics, #research, #life) */
$$("#nav a").forEach(a => a.addEventListener("click", e => {
  const href = a.getAttribute("href") || "";
  if (href.startsWith("#")) {
    e.preventDefault();
    page("public");
    $("#nav").classList.remove("open");
    setTimeout(() => {
      const target = $(href);
      if (target) target.scrollIntoView({ behavior:"smooth" });
    }, 50);
  }
}));
$("#togglePassword").onclick = () => {
  const p = $("#password");
  p.type = p.type === "password" ? "text" : "password";
  $("#togglePassword").textContent = p.type === "password" ? "Show" : "Hide";
};

/* ══════════════════════════════════════════════════════════
   LOGIN
   ══════════════════════════════════════════════════════════ */
$("#loginForm").addEventListener("submit", async e => {
  e.preventDefault();
  const email = $("#email").value.trim();
  const pw    = $("#password").value.trim();
  const errEl = $("#loginError");
  errEl.textContent = "";
  if (!email || !pw) { errEl.textContent = "Please fill in both fields."; return; }
  errEl.textContent = "Signing in…";
  const d = await api("/api/login", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({ email, password: pw })
  });
  if (!d.ok) { errEl.textContent = d.error || "Login failed. Check credentials."; return; }
  errEl.textContent = "";
  currentUser = d;
  role = (d.role || "student").toLowerCase();
  if (!roles[role]) role = "student";
  launch();
});

/* ══════════════════════════════════════════════════════════
   LAUNCH DASHBOARD
   ══════════════════════════════════════════════════════════ */
function launch() {
  page("dash");
  const r = roles[role];
  const initials = currentUser?.name
    ? currentUser.name.split(" ").map(w => w[0]).join("").slice(0,2).toUpperCase()
    : r.initials;
  $("#profileButton").textContent = initials;
  $("#dashTopTitle").textContent  = r.title;
  const pill = $(".demo-pill");
  if (pill) pill.style.display = "none";
  renderNav();
  render("Overview");
}

/* ══════════════════════════════════════════════════════════
   NAV
   ══════════════════════════════════════════════════════════ */
function renderNav() {
  const n = $("#dashNav");
  n.innerHTML = roles[role].nav
    .map(([a, i], idx) =>
      `<button class="nav-item${idx===0?" active":""}" data-view="${a}">
        <span>${i}</span>${a}</button>`).join("");
  $$(".nav-item", n).forEach(b => b.onclick = () => {
    $$(".nav-item", n).forEach(x => x.classList.toggle("active", x===b));
    render(b.dataset.view);
    $("#sidebar").classList.remove("open");
  });
}

function navTo(view) {
  const btn = [...$$(".nav-item")].find(b => b.dataset.view === view);
  if (btn) btn.click();
}

/* ══════════════════════════════════════════════════════════
   TEMPLATE HELPERS
   ══════════════════════════════════════════════════════════ */
function metric(label, value, icon, foot) {
  return `<article class="metric">
    <div class="metric-top">${label}<span class="metric-icon">${icon}</span></div>
    <div class="metric-value">${value}</div>
    <div class="metric-foot">${foot}</div>
  </article>`;
}

function activityRow(icon, title, sub, time) {
  return `<div class="activity-row">
    <span class="activity-icon">${icon}</span>
    <div><b>${title}</b><small>${sub}</small></div>
    <span class="activity-time">${time}</span>
  </div>`;
}

function activityBox(rows) {
  return `<div class="activity">${rows.join("")}</div>`;
}

function panel(title, sub, body) {
  return `<section class="panel">
    <div class="panel-head"><div><h3>${title}</h3><p>${sub}</p></div></div>
    ${body}
  </section>`;
}

function scheduleList(items) {
  if (!items || !items.length)
    return `<p style="padding:20px;color:#8792a3">No timetable data available.</p>`;
  const dotColors = ["dot-purple","dot-mint","dot-peach","dot-blue"];
  return `<div class="schedule-list">
    ${items.slice(0,8).map((x,i) => `
    <div class="schedule-item">
      <span class="schedule-time">${fmtTime(x.start_time)}</span>
      <span class="schedule-dot ${dotColors[i%4]}"></span>
      <span><b>${esc(x.course_name)}</b>
      <small>${x.day_of_week||""} · ${x.room_number||"TBA"}
      ${x.faculty_name?" · "+esc(x.faculty_name):""}</small></span>
      <span class="schedule-tag">${x.course_code||"CLASS"}</span>
    </div>`).join("")}
  </div>`;
}

function dataTable(headings, rows) {
  return `<div style="overflow-x:auto">
  <table class="data-table">
    <thead><tr>${headings.map(h=>`<th>${h}</th>`).join("")}</tr></thead>
    <tbody>${rows.join("")||`<tr><td colspan="${headings.length}" style="text-align:center;color:#8792a3;padding:20px">No records found</td></tr>`}</tbody>
  </table></div>`;
}

function badge(s) {
  const ok  = new Set(["Active","Paid","Present","Selected","Registered"]);
  const warn= new Set(["Pending","Partial","Absent","Shortlisted"]);
  const cls = ok.has(s)?"status":warn.has(s)?"status warn":"status";
  return `<span class="${cls}">${s||"—"}</span>`;
}

function fmtTime(t) {
  if (!t) return "--";
  const s = String(t);
  return s.includes(":") ? s.slice(0,5) : t;
}

function fmt(d) { return d ? String(d).split("T")[0] : "—"; }

function esc(s) {
  if (s === null || s === undefined) return "—";
  if (s === "") return "";
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function todayStr() {
  return new Date().toLocaleDateString("en-IN",
    {weekday:"long",day:"numeric",month:"short",year:"numeric"}).toUpperCase();
}

function welcomeBar(eyebrow, title, sub) {
  return `<div class="dash-welcome">
    <div><div class="eyebrow"><span class="pulse"></span> ${eyebrow}</div>
    <h1>${title}</h1><p>${sub}</p></div>
    <span class="dash-date">${todayStr()}</span>
  </div>`;
}

/* ══════════════════════════════════════════════════════════
   RENDER ROUTER
   ══════════════════════════════════════════════════════════ */
async function render(view) {
  if (view === "Students") { _sPage = 1; _sQ = ""; _sDept = ""; }
  if (view === "Courses")  { _cQ = ""; }
  $("#crumb").textContent = "WORKSPACE / " + view.toUpperCase();
  const c = $("#dashContent");
  c.innerHTML = `<div style="padding:60px;text-align:center;color:#8792a3;font-size:14px">
    Loading ${view}…</div>`;
  try {
    const map = {
      "Overview":           renderOverview,
      "Students":           renderStudents,
      "Faculty":            renderFaculty,
      "Departments":        renderDepts,
      "Courses":            renderCourses,
      "Timetable":          renderTimetable,
      "Hostel":             renderHostel,
      "Library":            renderLibrary,
      "Placements":         renderPlacements,
      "Reports":            renderReports,
      "SQL Console":        renderSQL,
      "My courses":         renderMyCourses,
      "Attendance register":renderAttReg,
      "Enter marks":        renderEnterMarks,
      "My profile":         renderMyProfile,
      "Attendance":         renderMyAttendance,
      "Marks & transcript": renderMyMarks,
      "Fee ledger":         renderFees,
    };
    if (map[view]) await map[view](c);
    else c.innerHTML = `<div style="padding:40px;color:#8792a3">Module: ${view}</div>`;
  } catch (ex) {
    c.innerHTML = `<div style="padding:40px;color:#e55;font-size:14px"><b>⚠ Error:</b> ${esc(ex.message)}</div>`;
    console.error("render", view, ex);
  }
  bindToast();
}

/* ══════════════════════════════════════════════════════════
   ADMIN OVERVIEW
   ══════════════════════════════════════════════════════════ */
async function renderOverview(c) {
  if (role === "faculty") { await renderFacultyOverview(c); return; }
  if (role === "student") { await renderStudentOverview(c); return; }

  const stats = await api("/api/admin/stats");

  c.innerHTML = welcomeBar("ADMIN WORKSPACE", roles.admin.title, roles.admin.sub)
  + `<div class="metric-grid">
      ${metric("Enrolled students",  (stats.students||0).toLocaleString(),  "♙", "Active students across all programs")}
      ${metric("Faculty members",    (stats.faculty||0).toLocaleString(),   "♧", "Teaching and research staff")}
      ${metric("Pending fees",       (stats.fee_pending||0).toLocaleString(),"₹", "Fee records due or partial")}
      ${metric("Placement drives",   (stats.placement_drives||0).toLocaleString(),"↗","Upcoming company drives")}
    </div>
    <div class="content-grid">
      ${panel("Campus at a glance","Live data from PostgreSQL 18",
        activityBox([
          activityRow("♙","Students",`${stats.students||0} active · ${stats.departments||0} departments`,"Live"),
          activityRow("♧","Faculty",`${stats.faculty||0} staff members`,"Live"),
          activityRow("▣","Library",`${stats.lib_active_loans||0} active loans · ${stats.total_books||0} books`,"Live"),
          activityRow("⌂","Hostel",`${stats.hostel_residents||0} residents allocated`,"Live"),
          activityRow("↗","Placements",`${stats.placement_drives||0} upcoming drives`,"Live"),
          activityRow("₹","Fees",`${stats.fee_pending||0} pending / partial`,"Live"),
        ])
      )}
      ${panel("Quick actions","Jump to any module",
        `<div class="quick-actions">
          ${["Students","Faculty","Departments","Courses","Library","Placements","Reports","SQL Console"]
            .map(x => `<button class="quick-action" onclick="navTo('${x}')">${x} ↗</button>`).join("")}
        </div>`
      )}
    </div>
    <div class="content-grid">
      ${panel("Campus snapshot","Live counts from database",
        dataTable(["Module","Count","Status"],[
          `<tr><td>Students</td><td><b>${stats.students||0}</b></td><td>${badge("Active")}</td></tr>`,
          `<tr><td>Faculty</td><td><b>${stats.faculty||0}</b></td><td>${badge("Active")}</td></tr>`,
          `<tr><td>Departments</td><td><b>${stats.departments||0}</b></td><td>${badge("Active")}</td></tr>`,
          `<tr><td>Courses</td><td><b>${stats.courses||0}</b></td><td>${badge("Active")}</td></tr>`,
          `<tr><td>Hostel residents</td><td><b>${stats.hostel_residents||0}</b></td><td>${badge("Active")}</td></tr>`,
        ])
      )}
      ${panel("System info","Database & platform",
        activityBox([
          activityRow("⌘","PostgreSQL 18","university_digital_twin database","Connected"),
          activityRow("♙","Programs","B.Tech · M.Tech · MBA · MCA · Ph.D","Active"),
          activityRow("▦","Departments",`${stats.departments ?? 0} academic departments`,"Active"),
          activityRow("▤","Courses",`${stats.courses ?? 0} courses across all programs`,"Active"),
        ])
      )}
    </div>`;
}

/* ── FACULTY OVERVIEW ── */
async function renderFacultyOverview(c) {
  const fid = currentUser?.linked_id;
  const fname = currentUser?.name || "Faculty";

  let fd = {}, tt = {};
  if (fid) {
    [fd, tt] = await Promise.all([
      api(`/api/faculty/${fid}`),
      api(`/api/timetable?faculty_id=${fid}`)
    ]);
  }

  const courses   = fd.courses || [];
  const ttSlots   = tt.timetable || [];
  const todayShort = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][new Date().getDay()];
  const todayClasses = ttSlots.filter(x => (x.day_of_week||"").startsWith(todayShort));

  c.innerHTML = welcomeBar("FACULTY WORKSPACE", `Welcome, ${fname.split(" ")[0]}`, roles.faculty.sub)
  + `<div class="metric-grid">
      ${metric("My courses",    courses.length,  "▤","Assigned teaching load")}
      ${metric("Students",      courses.reduce((a,x)=>a+Number(x.enrolled||0),0),"♙","Across your courses")}
      ${metric("Timetable slots",ttSlots.length, "▦","Scheduled class slots")}
      ${metric("Today's classes",todayClasses.length,"◷","Classes today")}
    </div>
    <div class="content-grid">
      ${panel("Today's schedule","Live timetable", scheduleList(todayClasses.length?todayClasses:ttSlots))}
      ${panel("My courses","Assigned teaching load",
        courses.length
          ? activityBox(courses.slice(0,6).map(x =>
              activityRow("▤", `${esc(x.course_code)} — ${esc(x.course_name)}`,
                `${x.enrolled||0} students · Sem ${x.semester_number||""} · ${x.credits||0} cr`,
                badge(x.course_type||"Active"))))
          : `<p style="padding:20px;color:#8792a3">No courses assigned. Check faculty ID.</p>`
      )}
    </div>
    <div class="content-grid">
      ${panel("Quick actions","Teaching shortcuts",
        `<div class="quick-actions">
          ${["My courses","Timetable","Attendance register","Enter marks","Students"]
            .map(x=>`<button class="quick-action" onclick="navTo('${x}')">${x} ↗</button>`).join("")}
        </div>`
      )}
      ${panel("Teaching workspace","Live assignment data",
        activityBox([
          activityRow("♧","Assigned courses",String(courses.length),"From faculty record"),
          activityRow("♙","Students across assigned courses",
            String(courses.reduce((a,x)=>a+Number(x.enrolled||0),0)),"From course enrolments"),
          activityRow("▦","Scheduled slots",String(ttSlots.length),"From timetable"),
          activityRow("◷","Today's classes",String(todayClasses.length),"From timetable"),
        ])
      )}
    </div>`;
}

/* ── STUDENT OVERVIEW ── */
async function renderStudentOverview(c) {
  const sid   = currentUser?.linked_id;
  const sname = currentUser?.name || "Student";

  let att={}, fees={}, lib={}, hostel={}, placements={}, tt={};
  if (sid) {
    [att, fees, lib, hostel, placements, tt] = await Promise.all([
      api(`/api/attendance/summary?student_id=${sid}`),
      api(`/api/fees?student_id=${sid}`),
      api(`/api/library/transactions?user_id=${sid}&user_type=Student&active=true`),
      api(`/api/hostel?student_id=${sid}`),
      api(`/api/placements/my?student_id=${sid}`),
      api(`/api/timetable?student_id=${sid}`)
    ]);
  }

  const attData  = att.attendance   || [];
  const feeData  = fees.fees        || [];
  const libData  = lib.transactions || [];
  const h        = (hostel.hostel   || [])[0];
  const placData = placements.registrations || [];
  const ttSlots  = tt.timetable || [];
  const todayShort = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][new Date().getDay()];
  const todayClasses = ttSlots.filter(x => (x.day_of_week||"").startsWith(todayShort));

  const avgAtt = attData.length
    ? Math.round(attData.reduce((a,x)=>a+Number(x.pct||0),0)/attData.length) : 0;
  const pendingFees = feeData.filter(f=>f.payment_status!=="Paid").length;

  c.innerHTML = welcomeBar("STUDENT WORKSPACE", `Welcome, ${sname.split(" ")[0]}`, roles.student.sub)
  + `<div class="metric-grid">
      ${metric("Avg attendance", `${avgAtt}%`, "◷", "Across all courses")}
      ${metric("Active lib loans", libData.length, "▣", "Books checked out")}
      ${metric("Pending fees",    pendingFees,    "₹", "Dues outstanding")}
      ${metric("Placements",      placData.length,"↗", "Applications made")}
    </div>
    <div class="content-grid">
      ${panel("Today's timetable","Your classes today", scheduleList(todayClasses.length?todayClasses:ttSlots))}
      ${panel("Attendance summary","Course-wise overview",
        attData.length
          ? activityBox(attData.slice(0,6).map(x =>
              activityRow("◷", esc(x.course_name),
                `${x.present||0}/${x.total||0} classes · ${x.pct||0}%`,
                Number(x.pct||0)>=75?"✓":"⚠")))
          : `<p style="padding:20px;color:#8792a3">No attendance records found.</p>`
      )}
    </div>
    <div class="content-grid">
      ${h
        ? panel("Hostel allocation","Your accommodation",
            activityBox([activityRow("⌂",`Room ${h.room_number}`,
              `${h.hostel_name} · Block ${h.block} · ${h.gender_type}`, "Active")]))
        : panel("Hostel","No allocation found",`<p style="padding:20px;color:#8792a3">No hostel allocation on record.</p>`)
      }
      ${panel("Placement applications","Your drives",
        placData.length
          ? activityBox(placData.slice(0,4).map(x =>
              activityRow("↗", esc(x.company_name),
                `₹${x.package_lpa||0}L · ${fmt(x.drive_date)}`,
                badge(x.selection_status))))
          : `<p style="padding:20px;color:#8792a3">No placement applications yet.</p>`
      )}
    </div>
    <div class="content-grid">
      ${panel("Quick actions","Student shortcuts",
        `<div class="quick-actions">
          ${["My profile","Attendance","Marks & transcript","Timetable","Fee ledger","Library","Placements"]
            .map(x=>`<button class="quick-action" onclick="navTo('${x}')">${x} ↗</button>`).join("")}
        </div>`
      )}
      ${panel("Recent fees","Fee ledger summary",
        feeData.length
          ? activityBox(feeData.slice(0,4).map(f =>
              activityRow("₹", f.fee_type,
                `₹${Number(f.amount||0).toLocaleString()} · Due ${fmt(f.due_date)}`,
                badge(f.payment_status))))
          : `<p style="padding:20px;color:#8792a3">No fee records found.</p>`
      )}
    </div>`;
}

/* ══════════════════════════════════════════════════════════
   STUDENTS (admin)
   ══════════════════════════════════════════════════════════ */
let _sPage=1, _sQ="", _sDept="";

async function renderStudents(c, pg, q, dept) {
  if (pg   !== undefined) _sPage = pg;
  if (q    !== undefined) _sQ    = q;
  if (dept !== undefined) _sDept = dept;

  const [data, depts] = await Promise.all([
    api(`/api/students?page=${_sPage}&q=${encodeURIComponent(_sQ)}&dept=${encodeURIComponent(_sDept)}`),
    api("/api/departments")
  ]);

  const total   = data.total || 0;
  const pages   = Math.max(1, Math.ceil(total/50));
  const studs   = data.students || [];
  const deptOpts= (depts.departments||[]).map(d =>
    `<option value="${esc(d.department_name)}"${_sDept===d.department_name?" selected":""}>${esc(d.department_name)}</option>`).join("");

  c.innerHTML = welcomeBar("ADMIN / STUDENTS","Student directory",`${total} students · Page ${_sPage} of ${pages}`)
  + panel("Search & filter","Filter by name, roll number or department",`
    <div style="display:flex;gap:10px;padding:15px 20px;flex-wrap:wrap;align-items:center">
      <input id="sQ" class="sql-input" style="flex:1;min-width:200px"
        placeholder="Name / roll number / email" value="${esc(_sQ)}"
        onkeydown="if(event.key==='Enter') renderStudents(document.getElementById('dashContent'),1,this.value,document.getElementById('sDept').value)">
      <select id="sDept" class="sql-input" style="min-width:180px">
        <option value="">All departments</option>${deptOpts}
      </select>
      <button class="btn btn-bright" style="padding:8px 18px"
        onclick="renderStudents(document.getElementById('dashContent'),1,document.getElementById('sQ').value,document.getElementById('sDept').value)">Search</button>
      <button class="btn btn-glass" style="padding:8px 14px" title="Reset filters"
        onclick="renderStudents(document.getElementById('dashContent'),1,'','')">Reset</button>
      ${role === "admin" ? `<button class="btn btn-glass" style="padding:8px 18px"
        onclick="showAddStudent()">+ Add student</button>` : ""}
    </div>`)
  + panel("Student records","Click any row to view full profile",
    dataTable(
      role === "admin" ? ["Roll No","Name","Department","Program","Yr/Sem","CGPA","Status","Action"] : ["Roll No","Name","Department","Program","Yr/Sem","CGPA","Status"],
      studs.map(s => `<tr style="cursor:pointer" onclick="showStudentDetail(${s.student_id})">
        <td><code>${esc(s.roll_number)}</code></td>
        <td><b>${esc(s.name)}</b></td>
        <td>${esc(s.department_name)}</td>
        <td>${esc(s.program_name)}</td>
        <td>${s.current_year||"—"}/${s.current_semester||"—"}</td>
        <td>${s.cgpa||"—"}</td>
        <td>${badge(s.status||"—")}</td>
        ${role === "admin" ? `<td><button class="quick-action" style="padding:4px 10px;font-size:11px;color:#f87171"
          onclick="event.stopPropagation();deleteStudent(${s.student_id},'${esc(s.name)}')">Delete</button></td>` : ""}
      </tr>`)
    )
    + `<div style="display:flex;gap:10px;padding:12px 20px">
        ${_sPage>1
          ? `<button class="quick-action" onclick="renderStudents(document.getElementById('dashContent'),${_sPage-1},'${_sQ}','${_sDept}')">← Prev</button>`:""}
        ${total>_sPage*50
          ? `<button class="quick-action" onclick="renderStudents(document.getElementById('dashContent'),${_sPage+1},'${_sQ}','${_sDept}')">Next →</button>`:""}
        <span style="font-size:12px;color:#8792a3;align-self:center">Showing ${studs.length} of ${total}</span>
      </div>`
  )
  + `<div id="studentDetailPanel"></div><div id="addStudentPanel"></div>`;
}

async function showStudentDetail(sid) {
  const el = $("#studentDetailPanel");
  if (!el) return;
  el.innerHTML = `<section class="panel"><div class="panel-head"><div><h3>Loading…</h3></div></div></section>`;
  const d = await api(`/api/students/${sid}`);
  const s = d.student || {};
  el.innerHTML = `<section class="panel">
    <div class="panel-head">
      <div><h3>${esc(s.first_name)} ${esc(s.last_name)}</h3>
      <p>${esc(s.roll_number)} · ${esc(s.department_name)} · ${esc(s.program_name)}</p></div>
      <button onclick="this.closest('section').remove()" style="background:none;border:none;font-size:22px;cursor:pointer;color:#8792a3">×</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:20px">
      <div>
        <h4 style="margin:0 0 10px;font-size:13px;color:#8792a3">PROFILE</h4>
        ${activityBox([
          activityRow("📧","Email",esc(s.email),""),
          activityRow("📱","Phone",esc(s.phone)||"—",""),
          activityRow("🎓","CGPA",s.cgpa||"—",""),
          activityRow("📅","DOB",fmt(s.dob),""),
          activityRow("🏛️","Year/Semester",`Year ${s.current_year} · Sem ${s.current_semester}`,""),
        ])}
      </div>
      <div>
        <h4 style="margin:0 0 10px;font-size:13px;color:#8792a3">ATTENDANCE</h4>
        ${activityBox((d.attendance||[]).slice(0,5).map(a =>
          activityRow("◷", esc(a.course_name), `${a.present}/${a.total}`, `${a.pct}%`))
          || [activityRow("◷","No data","—","—")])}
        <h4 style="margin:15px 0 10px;font-size:13px;color:#8792a3">FEE RECORDS</h4>
        ${activityBox((d.fees||[]).slice(0,4).map(f =>
          activityRow("₹", f.fee_type,
            `₹${Number(f.amount||0).toLocaleString()} · Due ${fmt(f.due_date)}`,
            badge(f.payment_status)))
          || [activityRow("₹","No records","—","—")])}
      </div>
    </div>
  </section>`;
  el.scrollIntoView({ behavior:"smooth" });
}

function showAddStudent() {
  const deptList = ["Computer Science","AI & Data Engineering","Electronics & Communication",
                    "Mechanical","Civil","Physics","Mathematics"];
  const progList = ["B.Tech","M.Tech","MBA","MCA","Ph.D"];
  const addEl = $("#addStudentPanel");
  if (!addEl) return;
  addEl.innerHTML = `<section class="panel">
    <div class="panel-head">
      <div><h3>Add new student</h3><p>Login credentials are auto-generated</p></div>
      <button onclick="this.closest('section').remove()" style="background:none;border:none;font-size:22px;cursor:pointer;color:#8792a3">×</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;padding:20px">
      ${[["first_name","First name","text"],["last_name","Last name","text"],
         ["email","Email","email"],["phone","Phone","text"],
         ["roll_number","Roll number","text"],["dob","Date of birth","date"]]
        .map(([id,lbl,type]) => `<div>
          <label style="font-size:12px;display:block;margin-bottom:4px;color:#8792a3">${lbl}</label>
          <input id="ns_${id}" type="${type}" class="sql-input" style="width:100%" placeholder="${lbl}">
        </div>`).join("")}
      <div>
        <label style="font-size:12px;display:block;margin-bottom:4px;color:#8792a3">Department</label>
        <select id="ns_department" class="sql-input" style="width:100%">
          ${deptList.map(d=>`<option>${d}</option>`).join("")}
        </select>
      </div>
      <div>
        <label style="font-size:12px;display:block;margin-bottom:4px;color:#8792a3">Program</label>
        <select id="ns_program" class="sql-input" style="width:100%">
          ${progList.map(p=>`<option>${p}</option>`).join("")}
        </select>
      </div>
      <div>
        <label style="font-size:12px;display:block;margin-bottom:4px;color:#8792a3">Gender</label>
        <select id="ns_gender" class="sql-input" style="width:100%">
          <option>Male</option><option>Female</option><option>Other</option>
        </select>
      </div>
    </div>
    <div style="padding:0 20px 20px;display:flex;gap:10px">
      <button class="btn btn-bright" style="padding:10px 24px" onclick="submitAddStudent()">Add student ↗</button>
      <button class="btn btn-glass" style="padding:10px 24px" onclick="this.closest('section').remove()">Cancel</button>
    </div>
    <div id="addStudentResult" style="padding:0 20px 15px"></div>
  </section>`;
  addEl.scrollIntoView({ behavior:"smooth" });
}

async function submitAddStudent() {
  const fields = ["first_name","last_name","email","phone","roll_number","dob","department","program","gender"];
  const body = {};
  fields.forEach(f => { const el = $(`#ns_${f}`); if (el) body[f] = el.value; });
  const d = await api("/api/students",{
    method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)
  });
  const r = $("#addStudentResult");
  if (!r) return;
  if (d.ok) {
    r.innerHTML = `<div style="background:#e8f8f0;border:1px solid #27ae60;padding:12px 16px;border-radius:8px;color:#155724">
      ✓ Student added! ID: ${d.student_id} · Auto-generated password: <b><code>${d.password}</code></b>
    </div>`;
    setTimeout(() => renderStudents($("#dashContent")), 3000);
  } else {
    r.innerHTML = `<div style="background:#fce;border:1px solid #e55;padding:12px 16px;border-radius:8px;color:#722">
      ✗ ${esc(d.error||"Unknown error")}
    </div>`;
  }
}

async function deleteStudent(sid, name) {
  if (!confirm(`Delete student ${name}? This cannot be undone.`)) return;
  const d = await api(`/api/students/${sid}`,{method:"DELETE"});
  if (d.ok) { toast(`Student ${name} deleted.`); renderStudents($("#dashContent")); }
  else toast("Delete failed: " + (d.error||"error"));
}

/* ══════════════════════════════════════════════════════════
   FACULTY LIST (admin)
   ══════════════════════════════════════════════════════════ */
async function renderFaculty(c) {
  const data = await api("/api/faculty");
  const facs = data.faculty || [];

  c.innerHTML = welcomeBar("ADMIN / FACULTY","Faculty directory",`${data.total||facs.length} faculty members`)
  + panel("Search faculty","Filter by name, department or designation",`
    <div style="display:flex;gap:10px;padding:15px 20px;flex-wrap:wrap">
      <input id="fQ" class="sql-input" style="flex:1;min-width:200px"
        placeholder="Name / email / department">
      <button class="btn btn-bright" style="padding:8px 18px"
        onclick="doFacultySearch()">Search</button>
    </div>`)
  + panel("Faculty members","All teaching staff",
    dataTable(
      ["ID","Name","Department","Designation","Qualification","Experience"],
      facs.map(f => `<tr>
        <td>${f.faculty_id}</td>
        <td><b>${esc(f.name)}</b></td>
        <td>${esc(f.department_name)}</td>
        <td>${esc(f.designation)||"—"}</td>
        <td>${esc(f.qualification)||"—"}</td>
        <td>${f.experience_years||0} yrs</td>
      </tr>`)
    )
  );
}

async function doFacultySearch() {
  const q = ($("#fQ")||{}).value || "";
  const data = await api(`/api/faculty?q=${encodeURIComponent(q)}`);
  const facs = data.faculty || [];
  const tbody = $(".data-table tbody");
  if (!tbody) return;
  tbody.innerHTML = facs.map(f => `<tr>
    <td>${f.faculty_id}</td>
    <td><b>${esc(f.name)}</b></td>
    <td>${esc(f.department_name)}</td>
    <td>${esc(f.designation)||"—"}</td>
    <td>${esc(f.qualification)||"—"}</td>
    <td>${f.experience_years||0} yrs</td>
  </tr>`).join("") || `<tr><td colspan="7" style="text-align:center;color:#8792a3;padding:20px">No results</td></tr>`;
}

/* ══════════════════════════════════════════════════════════
   DEPARTMENTS
   ══════════════════════════════════════════════════════════ */
async function renderDepts(c) {
  const data  = await api("/api/departments");
  const depts = data.departments || [];
  c.innerHTML = welcomeBar("ADMIN / DEPARTMENTS","Academic departments",`${depts.length} departments`)
  + `<div class="metric-grid">
      ${depts.map(d => metric(esc(d.department_name), d.student_count+" students","▦",
        `${d.faculty_count} faculty · ${d.course_count} courses`)).join("")}
    </div>`
  + panel("Department details","Live from PostgreSQL",
    dataTable(["Department","Faculty","Students","Courses"],
      depts.map(d => `<tr>
        <td><b>${esc(d.department_name)}</b></td>
        <td>${d.faculty_count}</td>
        <td>${d.student_count}</td>
        <td>${d.course_count}</td>
      </tr>`)
    )
  );
}

/* ══════════════════════════════════════════════════════════
   COURSES
   ══════════════════════════════════════════════════════════ */
let _cQ="";
async function renderCourses(c) {
  const [data, depts] = await Promise.all([
    api(`/api/courses?q=${encodeURIComponent(_cQ)}`),
    api("/api/departments")
  ]);
  const cs = data.courses || [];
  c.innerHTML = welcomeBar("ACADEMICS / COURSES","Course catalogue",`${data.total||cs.length} courses`)
  + panel("Search courses","Filter by course name or code",`
    <div style="display:flex;gap:10px;padding:15px 20px;flex-wrap:wrap">
      <input id="cQ" class="sql-input" style="flex:1;min-width:200px"
        placeholder="Course name or code" value="${esc(_cQ)}">
      <select id="cDept" class="sql-input" style="min-width:180px">
        <option value="">All departments</option>
        ${(depts.departments||[]).map(d=>`<option>${esc(d.department_name)}</option>`).join("")}
      </select>
      <button class="btn btn-bright" style="padding:8px 18px" onclick="doCourseSearch()">Search</button>
    </div>`)
  + panel("Courses","All courses from database",
    dataTable(
      ["Code","Course name","Department","Semester","Type","Credits","Enrolled"],
      cs.map(x => `<tr>
        <td><code>${esc(x.course_code)}</code></td>
        <td><b>${esc(x.course_name)}</b></td>
        <td>${esc(x.department_name)}</td>
        <td>${x.semester_number||"—"}</td>
        <td>${esc(x.course_type)||"—"}</td>
        <td>${x.credits||"—"}</td>
        <td>${x.enrolled||0}</td>
      </tr>`)
    )
  );
}

async function doCourseSearch() {
  const q    = ($("#cQ")||{}).value||"";
  const dept = ($("#cDept")||{}).value||"";
  _cQ = q;
  const data = await api(`/api/courses?q=${encodeURIComponent(q)}&dept=${encodeURIComponent(dept)}`);
  const tbody = $(".data-table tbody");
  if (!tbody) return;
  const cs = data.courses||[];
  tbody.innerHTML = cs.map(x => `<tr>
    <td><code>${esc(x.course_code)}</code></td>
    <td><b>${esc(x.course_name)}</b></td>
    <td>${esc(x.department_name)}</td>
    <td>${x.semester_number||"—"}</td>
    <td>${esc(x.course_type)||"—"}</td>
    <td>${x.credits||"—"}</td>
    <td>${x.enrolled||0}</td>
  </tr>`).join("")||`<tr><td colspan="7" style="text-align:center;color:#8792a3;padding:20px">No results</td></tr>`;
}

/* ══════════════════════════════════════════════════════════
   TIMETABLE
   ══════════════════════════════════════════════════════════ */
async function renderTimetable(c) {
  const sid = role==="student" ? currentUser?.linked_id : null;
  const fid = role==="faculty" ? currentUser?.linked_id : null;
  const url = sid ? `/api/timetable?student_id=${sid}`
            : fid ? `/api/timetable?faculty_id=${fid}`
            : "/api/timetable";
  const data = await api(url);
  const slots = data.timetable || [];
  const days  = ["Mon","Tue","Wed","Thu","Fri","Sat"];
  const grouped = {};
  slots.forEach(t => {
    const d = (t.day_of_week||"Other").slice(0,3);
    if (!grouped[d]) grouped[d] = [];
    grouped[d].push(t);
  });
  c.innerHTML = welcomeBar("ACADEMICS / TIMETABLE",
    fid?"Teaching schedule":sid?"My weekly timetable":"Campus timetable","")
  + days.filter(d=>grouped[d]).map(day =>
    panel(day,"Classes",`<div class="schedule-list">
      ${grouped[day].map((t,i) => `<div class="schedule-item">
        <span class="schedule-time">${fmtTime(t.start_time)}</span>
        <span class="schedule-dot ${ ["dot-purple","dot-mint","dot-peach","dot-blue"][i%4] }"></span>
        <span><b>${esc(t.course_name)}</b>
        <small>${t.room_number||"TBA"}${t.faculty_name?" · "+esc(t.faculty_name):""}</small></span>
        <span class="schedule-tag">${t.course_code||""}</span>
      </div>`).join("")}
    </div>`)
  ).join("")
  || `<p style="padding:40px;color:#8792a3">No timetable records found.</p>`;
}

/* ══════════════════════════════════════════════════════════
   HOSTEL (admin view)
   ══════════════════════════════════════════════════════════ */
async function renderHostel(c) {
  const data  = await api("/api/hostel");
  const hosts = data.hostel || [];
  c.innerHTML = welcomeBar("CAMPUS / HOSTEL","Hostel & facilities",`${hosts.length} hostel blocks`)
  + `<div class="metric-grid">
      ${hosts.map(h => metric(esc(h.hostel_name||h.block),
        (h.occupied||0)+" residents","⌂",
        `${h.total_rooms||0} rooms · ${h.total_capacity||0} capacity`)).join("")}
    </div>`
  + panel("Block summary","Hostel-wise occupancy",
    dataTable(["Hostel","Block","Type","Total rooms","Capacity","Occupied","Available"],
      hosts.map(h => `<tr>
        <td><b>${esc(h.hostel_name||"—")}</b></td>
        <td>${esc(h.block)||"—"}</td>
        <td>${esc(h.gender_type)||"—"}</td>
        <td>${h.total_rooms||0}</td>
        <td>${h.total_capacity||0}</td>
        <td>${h.occupied||0}</td>
        <td>${Math.max(0,(h.total_capacity||0)-(h.occupied||0))}</td>
      </tr>`)
    )
  );
}

/* ══════════════════════════════════════════════════════════
   LIBRARY (admin view)
   ══════════════════════════════════════════════════════════ */
async function renderLibrary(c) {
  const [books, txns] = await Promise.all([
    api("/api/library/books"),
    api("/api/library/transactions")
  ]);
  c.innerHTML = welcomeBar("CAMPUS / LIBRARY","Library & learning",
    `${books.total||0} books · ${(txns.transactions||[]).length} active loans`)
  + panel("Book catalogue","Search the library collection",`
    <div style="display:flex;gap:10px;padding:15px 20px">
      <input id="bQ" class="sql-input" style="flex:1" placeholder="Title / author / ISBN">
      <button class="btn btn-bright" style="padding:8px 18px" onclick="doBookSearch()">Search</button>
    </div>
    ${dataTable(["Title","Author","Category","Total copies","Available"],
      (books.books||[]).map(b => `<tr>
        <td><b>${esc(b.title)}</b></td>
        <td>${esc(b.author)}</td>
        <td>${esc(b.category)||"—"}</td>
        <td>${b.total_copies}</td>
        <td>${badge(b.available_copies>0?"Active":"Pending")} ${b.available_copies}</td>
      </tr>`)
    )}`)
  + panel("Active loans","Currently checked-out books",
    dataTable(["Title","User ID","Type","Issue date","Due date","Action"],
      (txns.transactions||[]).map(t => `<tr>
        <td><b>${esc(t.title)}</b></td>
        <td>${t.user_id}</td>
        <td>${t.user_type}</td>
        <td>${fmt(t.issue_date)}</td>
        <td>${fmt(t.due_date)}</td>
        <td><button class="quick-action" style="padding:4px 10px;font-size:11px"
          onclick="returnBook(${t.transaction_id})">Return</button></td>
      </tr>`)
    )
  );
}

async function doBookSearch() {
  const q = ($("#bQ")||{}).value||"";
  const books = await api(`/api/library/books?q=${encodeURIComponent(q)}`);
  const tbody = $(".data-table tbody");
  if (!tbody) return;
  tbody.innerHTML = (books.books||[]).map(b=>`<tr>
    <td><b>${esc(b.title)}</b></td><td>${esc(b.author)}</td>
    <td>${esc(b.category)||"—"}</td><td>${b.total_copies}</td><td>${b.available_copies}</td>
  </tr>`).join("");
}

async function returnBook(tid) {
  const d = await api("/api/library/return",{
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({transaction_id:tid})
  });
  if (d.ok) { toast(`Book returned. Fine: ₹${d.fine||0}`); renderLibrary($("#dashContent")); }
  else toast("Error: " + (d.error||"unknown"));
}

/* ══════════════════════════════════════════════════════════
   PLACEMENTS
   ══════════════════════════════════════════════════════════ */
async function renderPlacements(c) {
  const sid  = role==="student" ? currentUser?.linked_id : null;
  const [drives, mine] = await Promise.all([
    api("/api/placements/drives"),
    sid ? api(`/api/placements/my?student_id=${sid}`) : Promise.resolve({})
  ]);

  c.innerHTML = welcomeBar("CAREERS / PLACEMENTS","Placement drives",
    `${(drives.drives||[]).length} drives listed`)
  + (mine.registrations?.length
      ? panel("My applications","Your placement status",
          dataTable(["Company","Package","Drive date","Status"],
            (mine.registrations||[]).map(r => `<tr>
              <td><b>${esc(r.company_name)}</b></td>
              <td>₹${r.package_lpa||0}L</td>
              <td>${fmt(r.drive_date)}</td>
              <td>${badge(r.selection_status)}</td>
            </tr>`)
          )
        )
      : "")
  + panel("All placement drives","Company recruitment drives",
    dataTable(
      ["Company","Min CGPA","Package","Drive date","Registrations","Selected",...(sid?["Apply"]:["Action"])],
      (drives.drives||[]).map(d => `<tr>
        <td><b>${esc(d.company_name)}</b></td>
        <td>${d.eligibility_cgpa||0}</td>
        <td>₹${d.package_lpa||0}L</td>
        <td>${fmt(d.drive_date)}</td>
        <td>${d.registrations||0}</td>
        <td>${d.selected||0}</td>
        <td>${sid
          ? `<button class="quick-action" style="padding:4px 10px;font-size:11px"
               onclick="applyPlacement(${d.drive_id})">Apply ↗</button>`
          : `<span style="color:#8792a3;font-size:11px">Admin view</span>`
        }</td>
      </tr>`)
    )
  );
}

async function applyPlacement(did) {
  const sid = currentUser?.linked_id;
  const d = await api("/api/placements/register",{
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({student_id:sid, drive_id:did})
  });
  if (d.ok) { toast("Applied successfully!"); renderPlacements($("#dashContent")); }
  else toast("Error: " + (d.error||"already applied?"));
}

/* ══════════════════════════════════════════════════════════
   REPORTS (admin)
   ══════════════════════════════════════════════════════════ */
async function renderReports(c) {
  const stats = await api("/api/admin/stats");
  c.innerHTML = welcomeBar("ADMIN / REPORTS","Campus reports","Live summary from PostgreSQL 18")
  + `<div class="content-grid">
      ${panel("Enrollment summary","Live from DB",
        activityBox([
          activityRow("♙","Total students",`${stats.students||0} active`,"Live"),
          activityRow("♧","Total faculty",`${stats.faculty||0} members`,"Live"),
          activityRow("▦","Departments",stats.departments||0,"Live"),
          activityRow("▤","Courses",stats.courses||0,"Live"),
        ])
      )}
      ${panel("Campus services","Operational snapshot",
        activityBox([
          activityRow("₹","Pending dues",`${stats.fee_pending||0} records`,"Live"),
          activityRow("⌂","Hostel residents",`${stats.hostel_residents||0} allocated`,"Live"),
          activityRow("▣","Active lib loans",`${stats.lib_active_loans||0} books out`,"Live"),
          activityRow("↗","Open drives",`${stats.placement_drives||0} upcoming`,"Live"),
        ])
      )}
    </div>`;
}

/* ══════════════════════════════════════════════════════════
   SQL CONSOLE (admin)
   ══════════════════════════════════════════════════════════ */
async function renderSQL(c) {
  c.innerHTML = welcomeBar("ADMIN / SQL CONSOLE","Live SQL console",
    "Query the PostgreSQL 18 university_digital_twin database")
  + panel("Execute SQL","SELECT queries · DDL is blocked for safety",`
    <div style="padding:15px 20px">
      <textarea id="sqlInput" class="sql-input" rows="6"
        style="width:100%;font-family:monospace;font-size:13px;resize:vertical;box-sizing:border-box"
        onkeydown="handleSQLKeyDown(event)"
        placeholder="SELECT s.first_name, s.last_name, d.department_name
FROM student s
JOIN department d ON s.department_id = d.department_id
LIMIT 10"></textarea>
      <div style="display:flex;gap:10px;margin-top:10px;align-items:center;flex-wrap:wrap">
        <button class="btn btn-bright" style="padding:10px 24px" onclick="execSQL()">Run query ↗</button>
        <select id="sqlPresets" class="sql-input" style="flex:1;min-width:200px"
          onchange="document.getElementById('sqlInput').value=this.value;this.value=''">
          <option value="">— Sample queries —</option>
          <option value="SELECT COUNT(*) FROM student WHERE status='Active'">Count active students</option>
          <option value="SELECT d.department_name, COUNT(s.student_id) AS students FROM department d JOIN student s ON s.department_id=d.department_id GROUP BY d.department_name ORDER BY students DESC">Students per department</option>
          <option value="SELECT first_name, last_name, cgpa FROM student WHERE cgpa IS NOT NULL ORDER BY cgpa DESC LIMIT 10">Top 10 students by CGPA</option>
          <option value="SELECT fee_type, COUNT(*), SUM(amount) AS total FROM fee GROUP BY fee_type">Fee summary by type</option>
          <option value="SELECT co.company_name, pd.package_offered_lpa FROM placement_drive pd JOIN company co ON pd.company_id=co.company_id ORDER BY pd.package_offered_lpa DESC LIMIT 10">Top placement packages</option>
          <option value="SELECT title, author, available_copies FROM library_book WHERE available_copies=0">Fully checked-out books</option>
          <option value="SELECT * FROM department ORDER BY department_name">All departments</option>
          <option value="SELECT exam_type, COUNT(*), AVG(marks_obtained) FROM examination e JOIN marks m ON m.exam_id=e.exam_id GROUP BY exam_type">Average marks by exam type</option>
        </select>
      </div>
    </div>
    <div id="sqlResult" style="padding:0 20px 20px"></div>
  `);
}

function handleSQLKeyDown(e) {
  if (e.shiftKey && e.key === "Enter") {
    e.preventDefault();
    translateToSQL();
  }
}

async function translateToSQL() {
  const el = $("#sqlInput");
  if (!el) return;
  const prompt = el.value.trim();
  if (!prompt) return;

  const p = prompt.toLowerCase();
  let sql = null;

  // 1. Second / Third / Highest / Lowest Salary
  if (p.includes("second highest") || p.includes("2nd highest")) {
    sql = `SELECT faculty_id, first_name || ' ' || last_name AS faculty_name,
       designation, salary, department_id
FROM faculty
ORDER BY salary DESC
OFFSET 1 LIMIT 1;`;
  } else if (p.includes("third highest") || p.includes("3rd highest")) {
    sql = `SELECT faculty_id, first_name || ' ' || last_name AS faculty_name,
       designation, salary, department_id
FROM faculty
ORDER BY salary DESC
OFFSET 2 LIMIT 1;`;
  } else if (p.includes("highest salary") || p.includes("max salary") || p.includes("maximum salary")) {
    sql = `SELECT faculty_id, first_name || ' ' || last_name AS faculty_name,
       designation, salary, department_id
FROM faculty
ORDER BY salary DESC
LIMIT 1;`;
  } else if (p.includes("lowest salary") || p.includes("min salary")) {
    sql = `SELECT faculty_id, first_name || ' ' || last_name AS faculty_name,
       designation, salary, department_id
FROM faculty
ORDER BY salary ASC
LIMIT 1;`;
  }

  // 2. Only one student
  else if (p.includes("only one student") || p.includes("1 student") || p.includes("one student")) {
    if (p.includes("department")) {
      sql = `SELECT d.department_name, COUNT(s.student_id) AS student_count
FROM department d
JOIN student s ON d.department_id = s.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(s.student_id) = 1;`;
    } else if (p.includes("faculty")) {
      sql = `SELECT f.first_name || ' ' || f.last_name AS faculty_name,
       c.course_name, COUNT(sce.student_id) AS student_count
FROM faculty f
JOIN faculty_course fc ON f.faculty_id = fc.faculty_id
JOIN course c ON fc.course_id = c.course_id
JOIN student_course_enrollment sce ON c.course_id = sce.course_id
GROUP BY f.faculty_id, f.first_name, f.last_name, c.course_name
HAVING COUNT(sce.student_id) = 1;`;
    } else {
      sql = `SELECT c.course_code, c.course_name, COUNT(sce.student_id) AS enrolled_students
FROM course c
JOIN student_course_enrollment sce ON c.course_id = sce.course_id
GROUP BY c.course_id, c.course_code, c.course_name
HAVING COUNT(sce.student_id) = 1;`;
    }
  }

  // 3. faculty > X courses
  if (!sql) {
    let m = p.match(/faculty\s*(>|<|>=|<=|=)\s*(\d+)\s*(?:courses?|subjects?)?/);
    if (m && (p.includes("course") || p.includes("subject") || (!p.includes("student") && m[2]))) {
      const op = m[1], num = m[2];
      sql = `SELECT f.faculty_id, f.first_name || ' ' || f.last_name AS faculty_name,
       f.designation, d.department_name,
       COUNT(fc.course_id) AS total_courses_taught
FROM faculty f
JOIN department d ON f.department_id = d.department_id
JOIN faculty_course fc ON f.faculty_id = fc.faculty_id
GROUP BY f.faculty_id, f.first_name, f.last_name, f.designation, d.department_name
HAVING COUNT(fc.course_id) ${op} ${num}
ORDER BY total_courses_taught DESC;`;
    }
  }

  // 4. faculty > X students
  if (!sql || p.includes("student")) {
    let m2 = p.match(/faculty\s*(>|<|>=|<=|=)\s*(\d+)\s*students?/);
    if (m2) {
      const op = m2[1], num = m2[2];
      sql = `SELECT f.faculty_id, f.first_name || ' ' || f.last_name AS faculty_name,
       f.designation, d.department_name,
       COUNT(DISTINCT sce.student_id) AS total_students_taught
FROM faculty f
JOIN department d ON f.department_id = d.department_id
JOIN faculty_course fc ON f.faculty_id = fc.faculty_id
JOIN student_course_enrollment sce ON fc.course_id = sce.course_id
GROUP BY f.faculty_id, f.first_name, f.last_name, f.designation, d.department_name
HAVING COUNT(DISTINCT sce.student_id) ${op} ${num}
ORDER BY total_students_taught DESC;`;
    }
  }

  // 5. students cgpa > X
  if (!sql) {
    let m3 = p.match(/(?:students?.*)?cgpa\s*(>|<|>=|<=|=)\s*(\d+(?:\.\d+)?)/) || p.match(/students?\s*(>|<|>=|<=|=)\s*(\d+(?:\.\d+)?)\s*cgpa/);
    if (m3) {
      const op = m3[1], val = m3[2];
      sql = `SELECT roll_number, first_name || ' ' || last_name AS student_name,
       current_semester, cgpa, status
FROM student
WHERE cgpa ${op} ${val} AND status = 'Active'
ORDER BY cgpa DESC;`;
    }
  }

  // 6. attendance < X
  if (!sql) {
    let m4 = p.match(/attendance\s*(>|<|>=|<=|=)\s*(\d+)%?/);
    if (m4) {
      const op = m4[1], val = m4[2];
      sql = `SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name,
       c.course_code, c.course_name,
       COUNT(a.attendance_id) AS total_lectures,
       SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) AS attended_lectures,
       ROUND(100.0 * SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) / COUNT(a.attendance_id), 2) AS attendance_pct
FROM student s
JOIN attendance a ON s.student_id = a.student_id
JOIN course c ON a.course_id = c.course_id
GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, c.course_code, c.course_name
HAVING (100.0 * SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) ${op} ${val}
ORDER BY attendance_pct ASC;`;
    }
  }

  // 7. fee pending > X
  if (!sql) {
    let m5 = p.match(/fee(?:s)?.*?(>|<|>=|<=|=)\s*(\d+)/);
    if (m5) {
      const op = m5[1], val = m5[2];
      sql = `SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name,
       d.department_name, SUM(f.amount) AS total_pending_due
FROM student s
JOIN department d ON s.department_id = d.department_id
JOIN fee f ON s.student_id = f.student_id
WHERE f.payment_status IN ('Pending', 'Overdue')
GROUP BY s.roll_number, student_name, d.department_name
HAVING SUM(f.amount) ${op} ${val}
ORDER BY total_pending_due DESC;`;
    }
  }

  // 8. faculty courses list
  if (!sql && (p.includes("faculty") && (p.includes("course") || p.includes("subject") || p.includes("teach")))) {
    sql = `SELECT f.first_name || ' ' || f.last_name AS faculty_name,
       f.designation, d.department_name,
       c.course_code, c.course_name, c.credits,
       fc.academic_year, fc.semester_type
FROM faculty f
JOIN department d ON f.department_id = d.department_id
JOIN faculty_course fc ON f.faculty_id = fc.faculty_id
JOIN course c ON fc.course_id = c.course_id
ORDER BY d.department_name, faculty_name;`;
  }

  // 9. hostel vacancy
  if (!sql && (p.includes("hostel") || p.includes("room"))) {
    sql = `SELECT h.hostel_name, hr.room_number, hr.floor_number, hr.capacity,
       hr.current_occupancy, (hr.capacity - hr.current_occupancy) AS available_beds
FROM hostel h
JOIN hostel_room hr ON h.hostel_id = hr.hostel_id
WHERE hr.current_occupancy < hr.capacity
ORDER BY available_beds DESC;`;
  }

  // 10. toppers
  if (!sql && p.includes("topper")) {
    sql = `WITH ranked_scores AS (
    SELECT c.course_code, c.course_name, s.roll_number,
           s.first_name || ' ' || s.last_name AS student_name,
           m.marks_obtained,
           DENSE_RANK() OVER (PARTITION BY c.course_id ORDER BY m.marks_obtained DESC) AS course_rank
    FROM marks m
    JOIN examination e ON m.exam_id = e.exam_id
    JOIN course c ON e.course_id = c.course_id
    JOIN student s ON m.student_id = s.student_id
)
SELECT course_code, course_name, roll_number, student_name, marks_obtained AS topper_marks
FROM ranked_scores
WHERE course_rank = 1;`;
  }

  // Fallback to server API
  if (!sql) {
    try {
      const resp = await api("/api/ai/sql-translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      if (resp && resp.ok && resp.sql) {
        sql = resp.sql;
      }
    } catch (err) {}
  }

  if (sql) {
    el.value = sql;
  }
}

async function execSQL() {
  const q = ($("#sqlInput")||{}).value?.trim()||"";
  if (!q) { toast("Enter a SQL query first"); return; }
  const r = $("#sqlResult");
  if (r) r.innerHTML = `<p style="color:#8792a3;padding:10px">Running…</p>`;
  const d = await api("/api/sql",{
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({query:q})
  });
  if (!r) return;
  if (!d.ok) {
    r.innerHTML = `<div style="background:#fce;border:1px solid #e55;padding:12px;border-radius:8px;color:#722;font-family:monospace;font-size:13px">Error: ${esc(d.error||"unknown")}</div>`;
    return;
  }
  if (!d.rows?.length) { r.innerHTML=`<p style="color:#8792a3;padding:10px">Query returned no rows.</p>`; return; }
  r.innerHTML = `<div style="overflow-x:auto">
    <table class="data-table">
      <thead><tr>${(d.columns||[]).map(col=>`<th>${esc(col)}</th>`).join("")}</tr></thead>
      <tbody>${(d.rows||[]).map(row=>`<tr>${row.map(v=>`<td>${esc(String(v??"")||"")}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
    <p style="font-size:11px;color:#8792a3;margin-top:8px">${d.rows.length} rows${d.rows.length>=200?" (max 200 shown)":""}</p>
  </div>`;
}

/* ══════════════════════════════════════════════════════════
   FACULTY VIEWS
   ══════════════════════════════════════════════════════════ */
async function renderMyCourses(c) {
  const fid = currentUser?.linked_id;
  if (!fid) { c.innerHTML=`<p style="padding:40px;color:#e55">Faculty ID not found in session.</p>`; return; }
  const fd = await api(`/api/faculty/${fid}`);
  const courses = fd.courses||[];
  c.innerHTML = welcomeBar("FACULTY / COURSES","My courses",`${courses.length} courses assigned`)
  + `<div class="metric-grid">
      ${courses.map(x => metric(`${esc(x.course_code)} — ${esc(x.course_name)}`,x.enrolled+" students","▤",`Sem ${x.semester_number||"—"} · ${x.credits||0} credits`)).join("")}
    </div>`
  + panel("Course details","Assigned teaching load",
    dataTable(["Code","Course name","Type","Credits","Semester","Enrolled"],
      courses.map(x => `<tr>
        <td><code>${esc(x.course_code)}</code></td>
        <td><b>${esc(x.course_name)}</b></td>
        <td>${badge(x.course_type||"Core")}</td>
        <td>${x.credits||"—"}</td>
        <td>${x.semester_number||"—"}</td>
        <td>${x.enrolled||0}</td>
      </tr>`)
    )
  );
}

async function renderAttReg(c) {
  const fid = currentUser?.linked_id;
  if (!fid) { c.innerHTML=`<p style="padding:40px;color:#e55">Faculty ID not found.</p>`; return; }
  const fd  = await api(`/api/faculty/${fid}`);
  const courses = fd.courses||[];
  c.innerHTML = welcomeBar("FACULTY / ATTENDANCE","Attendance register","Mark attendance for your courses")
  + panel("Mark attendance","Select course and date, then mark students",`
    <div style="padding:15px 20px;display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <select id="attCourse" class="sql-input">
        <option value="">— Select course —</option>
        ${courses.map(x=>`<option value="${x.course_id}">${esc(x.course_code)} - ${esc(x.course_name)} (Sem ${x.semester_number||"—"})</option>`).join("")}
      </select>
      <input id="attDate" type="date" class="sql-input"
        value="${new Date().toISOString().split("T")[0]}">
      <button class="btn btn-bright" style="padding:8px 18px"
        onclick="loadAttReg(${fid})">Load students</button>
    </div>
    <div id="attRegister"></div>
  `);
}

async function loadAttReg(fid) {
  const cid = ($("#attCourse")||{}).value;
  if (!cid) { toast("Select a course first"); return; }
  const studs = await api(`/api/faculty/${fid}/students?course_id=${encodeURIComponent(cid)}`);
  const list  = studs.students||[];
  const reg   = $("#attRegister");
  if (!reg) return;
  reg.innerHTML = dataTable(
    ["Roll No","Name","Dept","Status for today"],
    list.map(s => `<tr>
      <td>${esc(s.roll_number)}</td>
      <td>${esc(s.name)}</td>
      <td>${esc(s.department_name)}</td>
      <td>
        <select class="sql-input att-status" data-sid="${s.student_id}" style="width:120px">
          <option value="Present">Present</option>
          <option value="Absent">Absent</option>
          <option value="Leave">Leave</option>
        </select>
      </td>
    </tr>`)
  )
  + `<div style="padding:15px 20px">
      <button class="btn btn-bright" style="padding:10px 24px"
        onclick="submitAttendance(${fid})">Submit attendance ↗</button>
    </div>`;
}

async function submitAttendance(fid) {
  const cid  = ($("#attCourse")||{}).value;
  const date = ($("#attDate")||{}).value;
  const records = [...$$(".att-status")].map(el => ({
    student_id: Number(el.dataset.sid),
    course_id:  Number(cid),
    status:     el.value,
    date
  }));
  const d = await api("/api/attendance/mark",{
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({faculty_id:fid, records})
  });
  if (d.ok) toast(`Attendance marked for ${d.marked} students.`);
  else toast("Error: " + (d.error||"unknown"));
}

async function renderEnterMarks(c) {
  const fid = currentUser?.linked_id;
  if (!fid) { c.innerHTML=`<p style="padding:40px;color:#e55">Faculty ID not found.</p>`; return; }
  const [fd, examsData] = await Promise.all([
    api(`/api/faculty/${fid}`),
    api(`/api/exams?faculty_id=${fid}`)
  ]);
  const courses = fd.courses||[];
  const exams   = examsData.exams||[];
  c.innerHTML = welcomeBar("FACULTY / MARKS","Enter marks","Submit marks for your examinations")
  + panel("Marks entry","Select exam, load students and submit marks",`
    <div style="padding:15px 20px;display:flex;gap:10px;flex-wrap:wrap">
      <select id="marksExam" class="sql-input" style="flex:1;min-width:200px">
        <option value="">— Select exam —</option>
        ${exams.map(e=>`<option value="${e.exam_id}" data-max="${e.max_marks}">${esc(e.exam_type)} · ${esc(e.academic_year||"")} · max ${e.max_marks}</option>`).join("")}
      </select>
      <button class="btn btn-bright" style="padding:8px 18px"
        onclick="loadMarksEntry(${fid})">Load students</button>
    </div>
    <div id="marksRegister"></div>
  `);
}

async function loadMarksEntry(fid) {
  const eid = ($("#marksExam")||{}).value;
  if (!eid) { toast("Select an exam first"); return; }
  const sel = $("#marksExam");
  const maxMarks = sel?.options[sel.selectedIndex]?.dataset?.max || 100;
  const [studs, existing] = await Promise.all([
    api(`/api/faculty/${fid}/students`),
    api(`/api/marks?exam_id=${eid}`)
  ]);
  const existMap = {};
  (existing.marks||[]).forEach(m => existMap[m.student_id] = m);
  const reg = $("#marksRegister");
  if (!reg) return;
  reg.innerHTML = dataTable(
    ["Roll No","Name","Marks (max "+maxMarks+")","Grade"],
    (studs.students||[]).map(s => `<tr>
      <td>${esc(s.roll_number)}</td>
      <td>${esc(s.name)}</td>
      <td><input class="sql-input marks-val" data-sid="${s.student_id}"
        style="width:80px" type="number" min="0" max="${maxMarks}"
        value="${existMap[s.student_id]?.marks_obtained||""}"></td>
      <td><input class="sql-input marks-grade" data-sid="${s.student_id}"
        style="width:60px" value="${existMap[s.student_id]?.grade||""}"></td>
    </tr>`)
  )
  + `<div style="padding:15px 20px">
      <button class="btn btn-bright" style="padding:10px 24px"
        onclick="submitMarks()">Save marks ↗</button>
    </div>`;
}

async function submitMarks() {
  const eid    = ($("#marksExam")||{}).value;
  const vals   = [...$$(".marks-val")];
  const grades = [...$$(".marks-grade")];
  const records = vals.filter(el=>el.value).map((el,i) => ({
    student_id:    Number(el.dataset.sid),
    exam_id:       Number(eid),
    marks_obtained:Number(el.value),
    grade:         grades[i]?.value||""
  }));
  const d = await api("/api/marks",{
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({records})
  });
  if (d.ok) toast(`Saved ${d.inserted} marks records.`);
  else toast("Error: " + (d.error||"unknown"));
}

/* ══════════════════════════════════════════════════════════
   STUDENT VIEWS
   ══════════════════════════════════════════════════════════ */
async function renderMyProfile(c) {
  const sid = currentUser?.linked_id;
  if (!sid) { c.innerHTML=`<p style="padding:40px;color:#e55">Student ID not found.</p>`; return; }
  const d = await api(`/api/students/${sid}`);
  const s = d.student||{};
  c.innerHTML = welcomeBar("STUDENT / PROFILE",
    `${s.first_name||""} ${s.last_name||""}`,
    `${s.roll_number||""} · ${s.department_name||""} · ${s.program_name||""}`)
  + `<div class="content-grid">
      ${panel("Personal details","Academic profile",
        activityBox([
          activityRow("📧","Email",     esc(s.email)||"—",""),
          activityRow("📱","Phone",     esc(s.phone)||"—",""),
          activityRow("🎓","CGPA",      s.cgpa||"—",""),
          activityRow("📅","DOB",       fmt(s.dob),""),
          activityRow("🏛️","Year / Sem",`Year ${s.current_year||"—"} · Sem ${s.current_semester||"—"}`,""),
          activityRow("📊","Status",    badge(s.status||"—"),""),
        ])
      )}
      ${panel("Recent marks","Latest results",
        (d.marks||[]).length
          ? activityBox((d.marks||[]).slice(0,6).map(m =>
              activityRow("✎", esc(m.course_name),
                `${esc(m.exam_name)} · ${m.marks_obtained}/${m.max_marks||100}`,
                m.grade||"—")))
          : `<p style="padding:20px;color:#8792a3">No marks data available.</p>`
      )}
    </div>`;
}

async function renderMyAttendance(c) {
  const sid = currentUser?.linked_id;
  if (!sid) { c.innerHTML=`<p style="padding:40px;color:#e55">Student ID not found.</p>`; return; }
  const data = await api(`/api/attendance/summary?student_id=${sid}`);
  const att  = data.attendance||[];
  const avg  = att.length ? Math.round(att.reduce((a,x)=>a+Number(x.pct||0),0)/att.length) : 0;

  c.innerHTML = welcomeBar("STUDENT / ATTENDANCE","Attendance overview","Course-wise attendance record")
  + `<div class="metric-grid">
      ${metric("Overall average",`${avg}%`,"◷","Across all courses")}
      ${metric("Courses tracked",att.length,"▤","Total courses")}
      ${metric("Below 75%",att.filter(x=>Number(x.pct)<75).length,"⚠","At-risk courses")}
      ${metric("Eligible (≥75%)",att.filter(x=>Number(x.pct)>=75).length,"✓","Exam eligible")}
    </div>`
  + panel("Course-wise attendance","Click row for details",
    dataTable(["Course","Present","Absent","Total","%","Eligibility"],
      att.map(a => `<tr>
        <td><b>${esc(a.course_name)}</b></td>
        <td>${a.present||0}</td>
        <td>${a.absent||0}</td>
        <td>${a.total||0}</td>
        <td><b>${a.pct||0}%</b></td>
        <td>${badge(Number(a.pct||0)>=75?"Active":"Pending")}</td>
      </tr>`)
    )
  );
}

async function renderMyMarks(c) {
  const sid = currentUser?.linked_id;
  if (!sid) { c.innerHTML=`<p style="padding:40px;color:#e55">Student ID not found.</p>`; return; }
  const data  = await api(`/api/marks?student_id=${sid}`);
  const marks = data.marks||[];
  c.innerHTML = welcomeBar("STUDENT / MARKS","Marks & transcript","All assessment results")
  + panel("Assessment results","Complete marks record",
    dataTable(["Course","Exam type","Marks","Max marks","Grade","Date"],
      marks.map(m => `<tr>
        <td><b>${esc(m.course_name)}</b></td>
        <td>${esc(m.exam_name||m.exam_type||"—")}</td>
        <td>${m.marks_obtained||"—"}</td>
        <td>${m.max_marks||"—"}</td>
        <td><b>${m.grade||"—"}</b></td>
        <td>${fmt(m.exam_date)}</td>
      </tr>`)
    )
  );
}

async function renderFees(c) {
  const sid = currentUser?.linked_id;
  if (!sid) { c.innerHTML=`<p style="padding:40px;color:#e55">Student ID not found.</p>`; return; }
  const data = await api(`/api/fees?student_id=${sid}`);
  const fees = data.fees||[];
  const total = fees.reduce((a,f)=>a+Number(f.amount||0),0);
  const paid  = fees.reduce((a,f)=>a+Number(f.paid_amount||0),0);

  c.innerHTML = welcomeBar("STUDENT / FEES","Fee ledger","Your complete fee record")
  + `<div class="metric-grid">
      ${metric("Total fees",    "₹"+total.toLocaleString(),"₹","All categories")}
      ${metric("Paid",          "₹"+paid.toLocaleString(), "✓","Amount settled")}
      ${metric("Outstanding",   "₹"+(total-paid).toLocaleString(),"⚠","Remaining balance")}
      ${metric("Records",       fees.length,"▤","Fee entries")}
    </div>`
  + panel("Fee details","Complete fee ledger",
    dataTable(["Type","Amount","Paid","Due date","Payment date","Status"],
      fees.map(f => `<tr>
        <td><b>${f.fee_type}</b></td>
        <td>₹${Number(f.amount||0).toLocaleString()}</td>
        <td>₹${Number(f.paid_amount||0).toLocaleString()}</td>
        <td>${fmt(f.due_date)}</td>
        <td>${fmt(f.payment_date)}</td>
        <td>${badge(f.payment_status)}</td>
      </tr>`)
    )
  );
}

/* ══════════════════════════════════════════════════════════
   SIGN OUT / PROFILE / MOBILE
   ══════════════════════════════════════════════════════════ */
$("#signOut").onclick = async () => {
  await api("/api/logout",{method:"POST"});
  currentUser = null; role = "admin"; page("public");
};
$("#profileButton").onclick = () => toast("Signed in as: " + (currentUser?.name||"—") + " (" + role + ")");
$("#mobileMenu").onclick    = () => $("#sidebar").classList.toggle("open");
$("#menuBtn").onclick       = () => $("#nav").classList.toggle("open");
$$(".theme-btn").forEach(b => b.onclick = () => document.body.classList.toggle("dark-mode"));

/* ── TOAST ── */
function bindToast() { $$("[data-toast]").forEach(b => b.onclick = () => toast(b.dataset.toast)); }
function toast(s) {
  const t = $("#toast"); t.textContent = s; t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 2800);
}

/* ══════════════════════════════════════════════════════════
   REVEAL ANIMATION  (original)
   ══════════════════════════════════════════════════════════ */
const obs = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add("visible"); obs.unobserve(e.target); }
}), { threshold:.12 });
$$(".reveal").forEach(e => obs.observe(e));
window.addEventListener("scroll", () => $("#header").classList.toggle("scrolled", scrollY > 10));

/* ══════════════════════════════════════════════════════════
   CAMPUS 3D TILT  (original)
   ══════════════════════════════════════════════════════════ */
const art3d = $("#campus3d");
$("#heroArt").addEventListener("mousemove", e => {
  if (matchMedia("(prefers-reduced-motion:reduce)").matches) return;
  const r = e.currentTarget.getBoundingClientRect();
  const x = (e.clientX-r.left)/r.width-.5, y = (e.clientY-r.top)/r.height-.5;
  art3d.style.transform = `rotateX(${-y*7}deg) rotateY(${x*8}deg)`;
});
$("#heroArt").addEventListener("mouseleave", () => art3d.style.transform = "");

/* ══════════════════════════════════════════════════════════
   PUBLIC PAGE — DETAIL PANELS
   Keys match EXACTLY the <b> text inside each clickable
   element in index.html. Live stats loaded from the API.
   ══════════════════════════════════════════════════════════ */

let _campusStats = null;
async function getCampusStats() {
  if (_campusStats) return _campusStats;
  _campusStats = await api("/api/admin/stats");
  return _campusStats;
}

const publicDetails = {
  /* Feature cards & hero chips */
  "campus spaces": {
    eyebrow:"01 / CAMPUS SPACES", title:"A campus built for possibility",
    intro:"Our university brings together learning, research and daily student life across a multi-building campus.",
    facts:[
      ["▦","academic departments","Computer Science, AI & Data Engineering, Electronics, Mechanical, Civil, Physics and Mathematics — each with dedicated teaching blocks, labs and faculty offices."],
      ["⌘","Labs & computing centres","Modern computing labs for programming, data analysis, simulation and electronics prototyping — fully equipped for AI/ML and project work."],
      ["♙","Student support hub","Academic advisors, examination cell, scholarship office, student welfare centre and all administrative services — all under one roof."],
      ["⌂","Everyday campus life","Canteen, sports complex, hostel blocks, medical centre, gym, open amphitheatre and bus transport services for day scholars."]
    ]
  },
  "campus facilities": {
    eyebrow:"01 / CAMPUS FACILITIES", title:"Campus facilities & spaces",
    intro:"Everything you need — from classrooms and computing labs to sports facilities, hostel blocks and the library — is right here on campus.",
    facts:[
      ["▦","Teaching spaces","Lecture theatres, seminar halls, tutorial rooms and open-plan learning areas across all department blocks."],
      ["⌘","Technology labs","High-spec computing labs, electronics workbenches, AI research clusters and digital fabrication rooms."],
      ["⌂","Hostel blocks","Aryabhata Hostel (Boys) and Kalpana Chawla Hostel (Girls) — Wi-Fi, hot water, common rooms and 24-hour security."],
      ["♙","Sports & wellness","Cricket ground, basketball and volleyball courts, gym, yoga studio and open sports fields."]
    ]
  },
  "research & innovation": {
    eyebrow:"02 / RESEARCH & INNOVATION", title:"Research with real purpose",
    intro:"Faculty and students collaborate on applied research in AI, Data Engineering, Electronics, Computing and Mathematics — turning coursework into projects with real-world impact.",
    facts:[
      ["⌘","AI & Data Science","GPU computing lab for machine learning, deep learning, NLP and large-scale data engineering experiments."],
      ["✳","Project-based learning","Every programme includes a major project semester — faculty-guided, industry-relevant and often leading to publications or internships."],
      ["♧","Faculty researchers","Our faculty bring expertise across computing, engineering, mathematics and related disciplines, guiding students through coursework and research."],
      ["↗","From idea to opportunity","Research output leads directly to placement advantages — companies actively recruit students with strong project and research backgrounds."]
    ]
  },
  "campus life": {
    eyebrow:"03 / CAMPUS LIFE", title:"Find your people and place",
    intro:"Campus life offers opportunities to join technical clubs, cultural events, hostel communities and placement preparation activities.",
    facts:[
      ["♙","Student clubs & societies","Technical clubs (coding, robotics, AI), cultural societies, sports teams and department student councils."],
      ["▣","Library & learning","A fully stocked library with thousands of books, e-resources and quiet study zones — open 6 days a week."],
      ["✦","Annual events & fests","TechFest, CulturalFest, Hackathons, Paper Presentations and inter-college competitions through the year."],
      ["↗","Placement preparation","Mock interviews, aptitude training, resume workshops and career guidance events run by the placement cell."]
    ]
  },
  "student experience": {
    eyebrow:"03 / STUDENT EXPERIENCE", title:"The student experience",
    intro:"University is more than a degree — it's the community you build, the skills you develop and the experiences that shape who you become.",
    facts:[
      ["♙","Peer learning","Study groups, peer mentoring and collaborative lab sessions make learning richer and more effective."],
      ["✦","Beyond the classroom","Guest lectures, industry visits, workshops, international webinars and cultural exchange programmes."],
      ["⌂","Hostel life","Living on campus builds independence, friendship and lifelong networks — both hostels have active student communities."],
      ["↗","Career-readiness","The placement cell starts career preparation from Year 2 — aptitude, communication, coding and interview skills."]
    ]
  },

  /* Academic list items — keys match exact <b> text */
  "courses & programmes": {
    eyebrow:"ACADEMICS / PROGRAMMES", title:"Courses & programmes",
    intro:"Explore courses and programmes spanning foundational sciences, engineering, computing, AI, data science and management.",
    facts:[
      ["▦","Degree programmes","B.Tech (4 years) · M.Tech (2 years) · MBA (2 years) · MCA (3 years) · Ph.D — subject to the programmes available in the university catalogue."],
      ["▤","Course catalogue","Core theory, lab practicals and electives — structured semester by semester with clear learning outcomes for every course."],
      ["♧","Faculty-led teaching","Each course is delivered by a qualified faculty member with relevant industry or research experience."],
      ["◷","Semester system","Two semesters per year — each with Internal Assessment 1, Internal Assessment 2 and an End-Term Examination."]
    ]
  },
  "timetable & attendance": {
    eyebrow:"ACADEMICS / SCHEDULE", title:"Timetable & attendance",
    intro:"Your personalised timetable shows every lecture, lab and tutorial for the week. Attendance is marked digitally by faculty after each class session and is immediately visible in your portal.",
    facts:[
      ["◷","Weekly class schedule","Mon–Sat schedule of lectures, labs and tutorials — room numbers, faculty and timings shown in your student portal."],
      ["☷","Digital attendance marking","Faculty mark attendance on the portal after each class. Students can check their course-wise attendance any time."],
      ["✓","75% attendance rule","Students must maintain at least 75% attendance per course to be eligible for the End-Term Examination."],
      ["⚠","Below 75% — act now","Students falling below 75% receive alerts. Check your attendance under the Attendance section in your student workspace."]
    ]
  },
  "assessments & results": {
    eyebrow:"ACADEMICS / ASSESSMENT", title:"Assessments & results",
    intro:"Academic performance is measured through internal assessments, practical lab work and an End-Term Examination — all your marks and grades are visible in real time through your student portal.",
    facts:[
      ["✎","Marks breakdown","Internal Assessment 1 (30) + Internal Assessment 2 (30) + End-Term Exam (40) = 100 marks per course."],
      ["▤","Grade scale","O (90+) · A+ (85+) · A (75+) · B+ (65+) · B (55+) · C (45+) · F (below 45) — grades assigned per course per semester."],
      ["▣","Live transcript","Your complete marks and grade record is available in real time under Marks & Transcript in your student workspace."],
      ["◷","Examination schedule","Exam dates, hall allocations and seating are published on the academic calendar at least 30 days in advance."]
    ]
  },
  "student & faculty services": {
    eyebrow:"CAMPUS PORTAL / SERVICES", title:"Student & faculty services",
    intro:"CampusOS gives every university member a personalised workspace — students manage their academic journey, faculty manage teaching, and admins oversee the whole institution.",
    facts:[
      ["♙","Student workspace","Courses, timetable, attendance per course, marks, fee ledger, library loans, hostel allocation and placement applications — all in one place."],
      ["♧","Faculty workspace","Teaching assignments, weekly timetable, attendance register (mark → saves to DB), marks entry (save → DB) and student progress tracking."],
      ["⌘","Admin workspace","Full campus overview — student & faculty directories, departments, courses, hostel, library, placement drives, reports and a live SQL console."],
      ["↗","Sign in to access","Use your university email and password to enter your personalised workspace. Credentials are issued by the administration."]
    ]
  },

  /* Service cards — keys match exact <b> text */
  "library & learning": {
    eyebrow:"CAMPUS SERVICES / LIBRARY", title:"Library & learning resources",
    intro:"The campus library holds thousands of books, journals and digital resources covering every programme. Issue, track due dates and return books through the portal — all updated in real time.",
    facts:[
      ["▣","Large book collection","Thousands of titles spanning CS, AI, Electronics, Mathematics, Management, Civil Engineering and general reference — all catalogued digitally."],
      ["↻","Issue & return system","Students can issue up to 3 books for 14 days. Returns are tracked digitally. Late returns attract a ₹5 per day fine."],
      ["⌂","Study spaces","Quiet reading zones, group study rooms and an open learning commons — available Mon–Sat, 8 AM to 8 PM."],
      ["▤","Your library in the portal","Sign in to view your currently issued books, due dates and outstanding fines — updated in real time from the database."]
    ]
  },
  "hostel & facilities": {
    eyebrow:"CAMPUS LIFE / ACCOMMODATION", title:"Hostel & campus facilities",
    intro:"On-campus accommodation is available in two hostels — Aryabhata Hostel for male students and Kalpana Chawla Hostel for female students. Allocations are managed by the administration each academic year.",
    facts:[
      ["⌂","Two hostel blocks","Aryabhata Hostel (Boys) and Kalpana Chawla Hostel (Girls) — Wi-Fi, hot water, common rooms, laundry and 24-hour security in both."],
      ["♙","Warden & welfare","Each hostel has a dedicated faculty warden for student welfare, facility management and grievance resolution."],
      ["⚙","Room facilities","Individual study desks, storage, fans/AC (selected rooms), power backup and regular housekeeping in all rooms."],
      ["🚌","Campus transport","University bus services connect campus to key city locations for day scholars — schedules available at the transport office."]
    ]
  },
  "fees & payments": {
    eyebrow:"CAMPUS SERVICES / FINANCE", title:"Fees & payments",
    intro:"Fee records covering Tuition, Hostel, Bus and Exam fees are maintained in the university system. Students can view their complete ledger, payment history and outstanding dues through the portal.",
    facts:[
      ["₹","Fee categories","Tuition Fee · Hostel Fee · Bus Transport Fee · Examination Fee — billed semester-wise with clear due dates."],
      ["▤","Real-time fee ledger","Your ledger shows total billed, amount paid, outstanding balance and payment dates — updated the moment payment is recorded."],
      ["✳","Scholarship support","Merit and need-based scholarships are available. Apply through the Scholarship Office with supporting documents."],
      ["✓","Payment confirmation","Once your payment is recorded by accounts, your fee status updates to 'Paid' or 'Partial' instantly in your portal."]
    ]
  },
  "placements & careers": {
    eyebrow:"CAREERS / PLACEMENTS", title:"Placements & career development",
    intro:"Our placement cell brings leading IT, analytics, engineering and management companies to campus. Students apply for drives and track their status — Registered → Shortlisted → Selected — from the portal.",
    facts:[
      ["↗","Campus recruitment drives","Companies including TCS, Infosys, Wipro and core engineering firms conduct on-campus drives — packages ranging from ₹4L to ₹15L+ per annum."],
      ["✦","Career preparation","Aptitude training, resume building, group discussions, mock interviews and communication skills workshops — from Year 2 onwards."],
      ["♙","Placement cell team","Dedicated placement officers coordinate with companies, schedule drives and provide end-to-end support for every registered student."],
      ["▤","Track your applications","Register for drives and track status (Registered → Shortlisted → Selected / Rejected) in real time from your student workspace."]
    ]
  }
};

const buildingDetails = [
  {
    eyebrow:"CAMPUS TOUR / ACADEMIC BLOCK", title:"Academic Block",
    intro:"The heart of campus learning — all 7 department offices, lecture halls, tutorial rooms and faculty chambers are here. Daily teaching, academic administration and student support all happen in this block.",
    facts:[
      ["▦","Lecture halls & classrooms","Large-capacity theatres and smaller seminar rooms for every course — equipped with projectors, audio systems and smart boards."],
      ["♧","Faculty offices","Find your course faculty for guidance, doubt-clearing, project discussions and mentoring on all weekdays."],
      ["▤","Department admin","Course registration, timetable queries, exam form submission, bonafide certificates and academic records are processed here."]
    ]
  },
  {
    eyebrow:"CAMPUS TOUR / RESEARCH CENTRE", title:"Research & Computing Centre",
    intro:"Where academic curiosity becomes applied innovation — AI labs, computing clusters, electronics workbenches and project rooms for student-faculty research.",
    facts:[
      ["⌘","AI & computing labs","High-performance GPU workstations, networked computing clusters and cloud-connected systems for AI, ML and data science work."],
      ["✳","Project & prototype rooms","Team project bays with whiteboards, hardware benches and 3D-print access — used for final-year projects and research work."],
      ["♧","Faculty research guidance","Mentors in each domain support literature review, experiment design, data analysis and research paper writing."]
    ]
  },
  {
    eyebrow:"CAMPUS TOUR / STUDENT SERVICES", title:"Student Services Building",
    intro:"Your one-stop hub for all non-academic university services — admissions, identity documents, examination administration, scholarship processing and student welfare support.",
    facts:[
      ["♙","Student affairs office","ID cards, bonafide certificates, transfer certificates, fee receipts, NOCs and all official university correspondence."],
      ["▤","Examination cell","Hall ticket issuance, seating charts, invigilation rosters, results publication and re-evaluation request processing."],
      ["↗","Scholarship & welfare","Application processing for merit and need-based scholarships, financial aid disbursement and student grievance redressal."]
    ]
  },
  {
    eyebrow:"CAMPUS TOUR / LIBRARY", title:"Library & Learning Commons",
    intro:"A quiet destination for deep study, group work and independent research — with thousands of books, journals, open study zones and a full circulation desk.",
    facts:[
      ["▣","Books & reference","Thousands of titles across all programmes — textbooks, reference books, journals and competitive exam resources."],
      ["⌂","Reading & study zones","Silent reading areas, group discussion rooms and an open learning commons — Mon–Sat, 8 AM to 8 PM."],
      ["↻","Issue & return desk","Issue up to 3 books for 14 days, renew or return here. Fine of ₹5 per day per book for late returns."]
    ]
  }
];

/* ══════════════════════════════════════════════════════════
   openDetail — async so it can show live DB stats
   ══════════════════════════════════════════════════════════ */
async function openDetail(key, tour=false) {
  /* Show overlay immediately */
  $("#detailOverlay").classList.remove("hidden");
  $("#detailOverlay").classList.toggle("dark-detail", document.body.classList.contains("dark-mode"));
  document.body.style.overflow = "hidden";
  $("#detailEyebrow").textContent = "CAMPUSOS · LOADING";
  $("#detailTitle").textContent   = "Fetching details…";
  $("#detailIntro").textContent   = "";
  $("#detailFacts").innerHTML     = `<div style="padding:16px 0;color:#8792a3;font-size:13px">Loading campus data…</div>`;

  let data;
  if (tour) {
    data = {
      eyebrow:"CAMPUS TOUR / INTERACTIVE", title:"Explore the campus",
      intro:"Click or tap any of the four buildings in the 3D campus model to discover what happens inside — teaching, research, student services or the library.",
      facts:[
        ["⌂","Academic Block","Classrooms, lecture halls, faculty offices and department administration offices."],
        ["✳","Research & Computing Centre","AI labs, GPU clusters, project rooms and electronics workbenches."],
        ["♙","Student Services Building","Admissions, examination cell, scholarship office and student welfare."],
        ["▣","Library & Learning Commons","Thousands of books, quiet study zones, group rooms and a circulation desk."]
      ]
    };
  } else {
    const raw = (key||"").toLowerCase().trim();
    data = publicDetails[raw];
    if (!data) {
      /* Partial match */
      const found = Object.keys(publicDetails).find(k =>
        raw.includes(k) || k.includes(raw) ||
        raw.replace(/&/g,"and").includes(k.replace(/&/g,"and")) ||
        k.replace(/&/g,"and").includes(raw.replace(/&/g,"and"))
      );
      data = found ? publicDetails[found] : {
        eyebrow:"CAMPUSOS / CAMPUS GUIDE", title: key||"Campus information",
        intro:"This area of university life is fully integrated into CampusOS. Sign in to your workspace to access complete details, records and services.",
        facts:[
          ["⌂","Available in your portal","All details and records for this service are accessible after signing in with your university credentials."],
          ["♙","Who it's for","Students, faculty and administrators each get a personalised view relevant to their role."],
          ["↗","Sign in to continue","Use your university email and password issued by the administration to access your workspace."]
        ]
      };
    }
  }

  /* Public information panels avoid institution-wide counts; totals belong in live admin views. */
/* Populate */
  $("#detailEyebrow").textContent = data.eyebrow;
  $("#detailTitle").textContent   = data.title;
  $("#detailIntro").textContent   = data.intro;
  $("#detailFacts").innerHTML = data.facts.map(x =>
    `<div class="detail-fact">
      <span class="detail-fact-icon">${x[0]}</span>
      <span><b>${x[1]}</b><small>${x[2]}</small></span>
    </div>`).join("");

  /* Visual panel */
  const visual = $("#detailVisual");
  visual.classList.toggle("tour-modal", tour);
  const raw2 = (key||"").toLowerCase();
  const kind = tour?"tour":
    raw2.includes("research")?"research":raw2.includes("library")?"library":
    raw2.includes("hostel")?"hostel":raw2.includes("fee")?"fees":
    raw2.includes("placement")||raw2.includes("career")?"careers":
    raw2.includes("campus life")||raw2.includes("community")?"community":"academic";
  visual.dataset.kind = kind;
  if (tour) {
    visual.innerHTML = `<div class="campus-3d tour-campus">${$("#campus3d").innerHTML}</div>
      <div class="tour-hint">SELECT ANY BUILDING TO EXPLORE</div>`;
    bindCampusBuildings(visual);
  } else {
    const icons={research:"✳",library:"▣",hostel:"⌂",fees:"₹",careers:"↗",community:"✦",academic:"▤"};
    visual.innerHTML = `<div class="topic-visual topic-${kind}">
      <span class="topic-orbit orbit-a"></span><span class="topic-orbit orbit-b"></span>
      <span class="topic-icon">${icons[kind]||"✳"}</span>
      <span class="topic-caption">CAMPUSOS · EXPLORE</span>
    </div>`;
  }
}

function closeDetail() {
  $("#detailOverlay").classList.add("hidden");
  document.body.style.overflow = "";
}

function bindCampusBuildings(root=document) {
  const idx = {"tower-a":0,"tower-b":1,"tower-c":2,"tower-d":3};
  $$(".tower", root).forEach(tower => {
    const cls = [...tower.classList].find(n => Object.prototype.hasOwnProperty.call(idx,n));
    const detail = buildingDetails[idx[cls]];
    if (!detail) return;
    tower.setAttribute("tabindex","0"); tower.setAttribute("role","button");
    tower.setAttribute("aria-label", detail.title);
    tower.setAttribute("title", `Explore: ${detail.title}`);
    tower.onclick   = e => { e.preventDefault(); e.stopPropagation(); openDetail(detail.title); };
    tower.onkeydown = e => { if(e.key==="Enter"||e.key===" "){ e.preventDefault(); tower.click(); } };
  });
}
bindCampusBuildings();

/* Wire all clickable public-page elements */
const featureMap = ["campus spaces","research & innovation","campus life"];
$$(".feature").forEach((card,i) => {
  card.style.cursor="pointer";
  card.setAttribute("tabindex","0"); card.setAttribute("role","button");
  const go = e => { if(e.target.closest("a")) e.preventDefault(); openDetail(featureMap[i]); };
  card.addEventListener("click", go);
  card.addEventListener("keydown", e => { if(e.key==="Enter"||e.key===" "){ e.preventDefault(); go(e); } });
});

const chipMap = ["campus facilities","research & innovation","student experience"];
$$(".art-chip").forEach((chip,i) => {
  chip.setAttribute("role","button"); chip.setAttribute("tabindex","0"); chip.style.cursor="pointer";
  const go = () => openDetail(chipMap[i]);
  chip.addEventListener("click", go);
  chip.addEventListener("keydown", e => { if(e.key==="Enter"||e.key===" "){ e.preventDefault(); go(); } });
});

$$(".academic-list>a").forEach(a => a.addEventListener("click", e => {
  e.preventDefault();
  openDetail((a.querySelector("b")?.textContent||a.textContent).trim().toLowerCase());
}));

$$(".service-card").forEach(b => b.addEventListener("click", e => {
  e.preventDefault();
  openDetail((b.querySelector("b")?.textContent||b.textContent).trim().toLowerCase());
}));

$$("[data-detail]").filter(el => !el.closest(".academic-list")&&!el.closest(".service-card"))
  .forEach(el => el.addEventListener("click", e => {
    e.preventDefault(); e.stopPropagation();
    const txt = (el.querySelector("b")?.textContent||el.textContent).trim().toLowerCase();
    openDetail(txt || "campus services");
  }));

/* Trust-row cards (Academics, Research, Campus services, Community) */
$$(".trust-row > div:not(.trust-intro)").forEach(item => {
  item.style.cursor = "pointer";
  item.setAttribute("tabindex", "0");
  item.setAttribute("role", "button");
  const bText = (item.querySelector("b")?.textContent || "").trim().toLowerCase();
  const map = {
    "academics": "courses & programmes",
    "research": "research & innovation",
    "campus services": "campus facilities",
    "community": "campus life"
  };
  const key = map[bText] || bText;
  const go = () => openDetail(key);
  item.addEventListener("click", go);
  item.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
});

$("#campusTour").addEventListener("click", () => openDetail("tour", true));
$("#detailClose").onclick = closeDetail;
$("#detailDone").onclick  = closeDetail;
$("#detailOverlay").addEventListener("click", e => { if(e.target===$("#detailOverlay")) closeDetail(); });
document.addEventListener("keydown", e => {
  if(e.key==="Escape"&&!$("#detailOverlay").classList.contains("hidden")) closeDetail();
});

/* Auto-load live credentials on login page */
async function loadQuickProfiles() {
  try {
    const d = await api("/api/quick-profiles");
    const profiles = d.profiles||{};
    const el = $("#loginError");
    if (!el || document.querySelector(".live-creds")) return;
    const admin = profiles.admin?.[0];
    const fac   = profiles.faculty?.[0];
    const stu   = profiles.students?.[0];
    const note  = document.createElement("div");
    note.className = "demo-note live-creds";
    note.style.cssText = "margin-top:14px;font-size:13px;line-height:2";
    note.innerHTML = `<b style="color:#8792a3;font-size:11px;letter-spacing:.05em">QUICK SIGN-IN — LIVE FROM DATABASE</b><br>
      ${admin?`🔐 <b>Admin:</b> <code>${admin.email}</code> / <code>${admin.password}</code><br>`:""}
      ${fac  ?`🧑‍🏫 <b>Faculty:</b> <code>${fac.email}</code> / <code>${fac.password}</code><br>`:""}
      ${stu  ?`🎓 <b>Student:</b> <code>${stu.email}</code> / <code>${stu.password}</code>`:""}`;
    el.after(note);
  } catch(e) {}
}
const loginObs = new MutationObserver(() => {
  if (!$("#loginPage").classList.contains("hidden") && !document.querySelector(".live-creds"))
    loadQuickProfiles();
});
loginObs.observe($("#loginPage"), {attributes:true, attributeFilter:["class"]});

