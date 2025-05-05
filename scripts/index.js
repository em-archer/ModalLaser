// elements
const HGSelect = document.getElementById('HG-select')
const LGSelect = document.getElementById('LG-select')
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
    (0 <= mTemp && mTemp < 10)
    && (0 <= nTemp && nTemp < 10)
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
HGSelect.href = `./?HG_${m}_${n}`
LGSelect.href = `./?LG_${m}_${n}`

// create table for orbital selection
for (let mTable = 0; mTable < 10; mTable += 1) {
  let tableRow = `<div style="background-color:hsl(${mTable * 50}, 100%, 80%)">`

  for (let nTable = 0; nTable < 10; nTable += 1) {
    let subshellSection = `<div class="subshell-container"><div class="links-container">`
    
    subshellSection += `<a 
        href="./?${mode}_${mTable}_${nTable}" 
        class="orbital" id="${mTable === m && nTable === n ? "selected-orbital" : ""}">${mTable}${nTable}
      </a>`

    subshellSection += `</div><div class='labels-container'>${mTable}${nTable}</div></div>`
    tableRow += subshellSection
  }

  tableRow += '</div>'
  selectTable.innerHTML += tableRow
}