// elements
const hermiteSelect = document.getElementById('HG-select')
const laguerreSelect = document.getElementById('LG-select')
const graphEl = document.getElementById('image')
const selectTable = document.getElementById('select-table')

// get info from url
const urlInfo = window.location.search

// settings
let m = 0
let n = 0
let mode = 'HG'

// ? on end of url in form of ?mode_m_n
if (urlInfo && urlInfo.length > 1) {
  const params = urlInfo.substring(1).split('_')
  let mTemp = parseInt(params[1])
  let nTemp = parseInt(params[2])
  let modeTemp = params[0]
  
  if (
    (0 < nTemp && nTemp < 5)
    && (0 <= mTemp && mTemp < 5)
    && (mode === 'HG' || mode === 'LG')
  ) {
    mode = modeTemp
    m = mTemp
    n = nTemp
  }
}

// set image
const path = `img/${mode}/${m}_${n}.png`
graphEl.src = path

// mark selected mode
document.getElementById(`${mode}-select`).id = 'selected-mode'

// set up links for mode selection
hermiteSelect.href = `./?HG_${m}_${n}`
laguerreSelect.href = `./?LG_${m}_${n}`


// create table for orbital selection
for (let mTable = 1; mTable < 5; mTable += 1) {
  let tableRow = `<div style="background-color:hsl(${mTable * 50}, 100%, 80%)">`

  for (let nTable = 1; nTable < 5; nTable += 1) {
    let subshellSection = `<div class="subshell-container"><div class="links-container">`
        
    subshellSection += `<a href="./?${mode}_${mTable}_${nTable}" 
    class="orbital" id="${mTable === m && nTable === n && ? "selected-orbital" : ""}">${mTable}${nTable}</a>`

    subshellSection += `</div><div class='labels-container'>${nTable}','${mTable}</div></div>`
    tableRow += subshellSection
  }

  tableRow += '</div>'
  selectTable.innerHTML += tableRow
}