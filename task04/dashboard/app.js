async function loadSummary(){
  const res = await fetch("../results/summary.json?cache=" + Date.now());
  if(!res.ok) throw new Error("Não consegui ler summary.json");
  return await res.json();
}

function stepStatus(entry, step){
  const s = (entry.steps||{})[step]||{};
  if(s.skipped) return "SKIP";
  return s.ok ? "OK" : "FAIL";
}

function tag(status){
  const cls = status==="OK" ? "tag ok" : status==="SKIP" ? "tag skip" : "tag fail";
  return `<span class="${cls}">${status}</span>`;
}

function link(path, text){
  if(!path) return "";
  const safe = path.replace(/^.*?task04\//, "../"); // normalize
  return `<a href="${safe}" target="_blank" rel="noreferrer">${text||"abrir"}</a>`;
}

function render(data){
  const q = document.getElementById("q").value.toLowerCase().trim();
  const step = document.getElementById("step").value;
  const status = document.getElementById("status").value;

  const rows = document.getElementById("rows");
  rows.innerHTML = "";

  const filtered = data.filter(e => {
    if(q && !(e.design||"").toLowerCase().includes(q)) return false;
    if(step){
      const st = stepStatus(e, step);
      if(status && st!==status) return false;
    } else {
      if(status){
        // any step matches chosen status
        const steps = ["vhd2vl","yosys_prep","sby","v2c","esbmc"];
        if(!steps.some(s => stepStatus(e, s)===status)) return false;
      }
    }
    return true;
  });

  document.getElementById("meta").textContent = `Itens: ${filtered.length} (de ${data.length})`;

  for(const e of filtered){
    const s = (st)=>tag(stepStatus(e, st));
    const notes = (e.notes||[]).join(" • ");
    const ast = (e.generated||{}).common_ast || "";
    rows.insertAdjacentHTML("beforeend", `
      <tr>
        <td><b>${e.design||""}</b></td>
        <td>${link(e.vhdl, "VHDL")}</td>
        <td>${link(e.spec, "spec.json")}</td>
        <td>${s("vhd2vl")}</td>
        <td>${s("yosys_prep")}</td>
        <td>${s("sby")}</td>
        <td>${s("v2c")}</td>
        <td>${s("esbmc")}</td>
        <td>${ast ? link(ast, "ast.json") : ""}</td>
        <td>${notes}</td>
      </tr>
    `);
  }
}

async function main(){
  const btn = document.getElementById("reload");
  const inputs = ["q","step","status"];
  for(const id of inputs){
    document.getElementById(id).addEventListener("input", ()=>main());
    document.getElementById(id).addEventListener("change", ()=>main());
  }
  btn.addEventListener("click", ()=>main());

  try{
    const data = await loadSummary();
    render(data);
  }catch(err){
    document.getElementById("meta").textContent = err.message;
  }
}
main();
