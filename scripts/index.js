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
    (0 < mTemp && mTemp < 5)
    && (0 < nTemp && nTemp < 5)
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

// subshell numbers to letters table
subshellTable = {
  0: 's',
  1: 'p',
  2: 'd',
  3: 'f',
  4: 'g',
  5: 'h',
  6: 'i'
}

// create table for orbital selection
for (let nTable = 1; nTable < 8; nTable += 1) {
  let tableRow = `<div style="background-color:hsl(${nTable * 50}, 100%, 80%)">`

  for (let lTable = 0; lTable < nTable; lTable += 1) {
    let subshellSection = `<div class="subshell-container"><div class="links-container">`

    for (let mTable = -lTable; mTable <= lTable; mTable += 1) {
      subshellSection += `<a 
        href="./?${mode}_${nTable}_${lTable}_${mTable}" 
        class="orbital" id="${nTable === n && lTable === l && mTable === m ? "selected-orbital" : ""}">${mTable}
      </a>`
    }

    subshellSection += `</div><div class='labels-container'>${nTable}${subshellTable[lTable]}</div></div>`
    tableRow += subshellSection
  }

  tableRow += '</div>'
  selectTable.innerHTML += tableRow
}