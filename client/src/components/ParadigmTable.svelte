<script>
    import { tick } from "svelte";
    import { Pulse } from "svelte-loading-spinners";

    export let data = null;

    let results = null;

    let word = "";
    let wc = "";
    let wc_extra = "";

    let state = "nothing";
    $: update_state(data);

    async function update_state(data) {
        if (data === null) {
            state = "nothing";
            await tick();
            return;
        }
        state = "awaiting";
        await tick();
        results = parse_data(await data);
        state = "done";
        await tick();
    }

    const TAG_TO_ENGLISH = {
        Inf: "Infinitive",
        Ind: "Indicative",
        Cond: "Conditional",
        Imprt: "Imperative",
    };

    class Entry {
        constructor() {
            this._is_empty = true;
            this._text = "";
        }

        get is_empty() {
            return this._is_empty;
        }

        set_text(text) {
            this._is_empty = false;
            this._text = text;
        }

        get_text() {
            return this._text;
        }
    }

    function reverse_spans(spans) {
        // TODO solve this in general
        if (spans[0] === 1 && spans[1] === 1) {
            // [1, 1] -> [1, 1]
            return [1, 1];
        } else if (spans[0] === 1 && spans[1] === 2) {
            // [1, 2] -> [2, 1]
            return [2, 1];
        } else if (spans[0] === 2 && spans[1] === 1) {
            // [2, 1] -> [1, 2]
            return [1, 2];
        } else {
            throw Error("unhandled case");
        }
    }

    function array2d(x, y) {
        return Array(y).fill(null).map(_ => Array(x).fill(undefined));
    }

    function *enumerate(list, start = 0) {
        for (let i = start; i < list.length; i++) {
            yield [i, list[i]];
        }
    }

    function group_by_length(lines) {
        let current_size = lines[0].length;
        let current_group = [lines[0]];
        const groups = [];
        for (let i = 1; i < lines.length; i++) {
            const current_line = lines[i];
            if (current_line.length !== current_size) {
                // this line's length is different, so make next group
                current_size = current_line.length;
                groups.push(current_group);
                current_group = [];
            }
            current_group.push(current_line);
        }
        return groups;
    }

    class Layout {
        constructor() {
            this.columns = [];
            this.rows = [];
            this.column_headers_rows = [[]];
        }

        column(...text) {
            // text = [abc, def]
            // [ [], [] ] --> [ [abc], [def] ]
            for (let i = 0; i < this.columns.length; i++) {
                this.column_headers_rows[i].push(text[i]);
            }
            return this;
        }

        row(text) {
            this.rows.push(text);
            return this;
        }
    }

    const _table_format = `
-|A|   B |C|
-|a|b1|b2|c|
1|
2|
    `;
    class MisalignedError extends Error {
        constructor(row, column, char, ...params) {
            super(...params);
            this.name = this.constructor.name;
            this.message = `Mis-aligned column in row ${row}. `
                + `Because "|" was found in this column on line 1, expected `
                + `"|" to be found in column ${column} but, but found ${char}.`;
        }
    }
    const MISALIGNED = (row, other_ch) => `mis-aligned column in row ${row}.`
        + ` "|" found in this column on line 1, but this line has character `
        + `"${other_ch}" in that column position`;
    function structurize(text) {
        let lines = text.split("\n");
        lines = lines.splice(1, lines.length);
        let [col_headers, row_headers] = group_by_length(lines);
        row_headers = row_headers.map(s => s.replaceAll("|", ""));

        const col_header_height = col_headers.length;
        const col_header_width = col_headers
            .map(ch => ch.split("|"))
            .reduce((prev, cur) => Math.max(prev, cur.length), 0);
        //console.log(`colum header dimensions: ${col_header_height} x ${col_header_width}`);

        // allocate `columns`
        const columns = Array(col_header_height).fill(0).map(_0 => []);

        let last_index = 0;
        const first_col_row = col_headers[0];
        for (let [i, ch] of enumerate(first_col_row)) {
            if (ch !== "|") {
                continue;
            }

            const first_col = first_col_row.slice(last_index, i);
            const to_be_pushed = [first_col];

            // find the other headers
            for (let j = 1; j < col_headers.length; j++) {
                const ch_other = col_headers[j][i];
                if (ch_other !== ch) {
                    throw new MisalignedError(j + 1, i, ch_other);
                }

                let other_col = col_headers[j].slice(last_index, i);
                to_be_pushed.push(other_col);
            }

            const to_be_pushed_splits = to_be_pushed.map(s => s.split("|"));
            const spans = to_be_pushed_splits.map(arr => arr.length);
            const rev_spans = reverse_spans(spans);

            for (let [t, arr] of enumerate(to_be_pushed_splits)) {
                for (let inner_idx = 0; inner_idx < arr.length; inner_idx++) {
                    columns[t].push({
                        text: arr[inner_idx],
                        span: rev_spans[t],
                    });
                }
            }

            last_index = i + 1;
        }

        return {
            row_headers,
            columns,
        };
    }

    let table = {
        caption: "caption",
        row_headers: ["1", "2"],
        columns: [
            [{text: "A", span: 1}, { text: "B", span: 2}, {text: "C", span: 1}],
            [{text: "_a", span: 1}, { text: "_b1", span: 1 }, {text: "_b2", span:1}, {text: "c", span:1}],
        ],
        data: [
            ["a", "b"],
            ["c", "d"],
        ],
    };

    const _inner_data = structurize(_table_format);
    console.log("partial table structure:", _inner_data);
    table = {
        caption: "caption (generated)",
        data: [
            ["a", "b"],
            ["c", "d"],
        ],
        ..._inner_data,
    };


    function parse_data(data) {
        const results = {};
        for (let [line, res] of data.result) {
            const firstplus = line.indexOf("+");
            const secondplus = line.indexOf("+", firstplus + 1);
            line = line.slice(secondplus + 1, line.length);

            if (line in results) {
                results[line] += ", " + res;
            } else {
                results[line] = res;
            }
        }
        word = results["Inf"];
        wc = "Verb";

        // TODO fjern former som ikke finnes
        // hvis en hel rad kan fjernes, fjern hele raden
        // hvis en hel kolonne kan fjernes, fjern hele kolonna,
        // ellers, sett inn "-"
        const remove_keys = [];
        for (let [k, v] of Object.entries(results)) {
            if (v === undefined) {
                remove_keys.push(k);
            }
        }
        return results;
    }

    function show(obj, key) {
        const res = obj[key];
        return res === undefined ? "-" : res;
    }
</script>

<hr>

<table>
    <caption>{table.caption}</caption>
    <thead>
        {#each table.columns as column_row}
            <tr>
                {#if table.row_headers}
                    <th></th>
                {/if}
                {#each column_row as { text, span }}
                    <th colspan={span}>{text}</th>
                {/each}
            </tr>
        {/each}
    </thead>
    <tbody>
        {#each table.data as row, i}
            <tr>
                {#if table.row_headers[i]}
                    <th>{table.row_headers[i]}</th>
                {/if}
                {#each row as col, i}
                    <td>{col}</td>
                {/each}
            </tr>
        {/each}
    </tbody>
</table>

<hr>

{#if state === "awaiting"}
    <Pulse color="#FF0000" size="28" unit="px" duration="1s" />
{:else if state === "done"}
    <h3>{word}: {wc}{wc_extra}</h3>

    <table>
        <caption>Personsbøyd</caption>
        <colgroup>
            <col>
            <col span="2" class="ind">
            <col class="cond">
            <col class="imperative">
            <col class="potential">
        </colgroup>
        <thead>
            <tr>
                <th class="expl">Mood</th>
                <th colspan="2" scope="colgroup">Indicative</th>
                <th scope="colgroup">Conditional</th>
                <th scope="colgroup">Imperative</th>
                <th scope="colgroup">Potential</th>
            </tr>
            <tr>
                <th class="expl">Tense</th>
                <th scope="col">Present</th>
                <th scope="col">Preterite</th>
                <th scope="col">Present</th>
                <th></th>
                <th scope="col">Present</th>
            </tr>
        </thead>
        <tr>
            <th>Sg1</th>
            <td>{results["Ind+Prs+Sg1"]}</td>
            <td>{results["Ind+Prt+Sg1"]}</td>
            <td>{results["Cond+Prs+Sg1"]}</td>
            <td>{results["Imprt+Sg1"]}</td>
            <td>{results["Pot+Prs+Sg1"]}</td>
        </tr>
        <tr>
            <th>Sg2</th>
            <td>{results["Ind+Prs+Sg2"]}</td>
            <td>{results["Ind+Prt+Sg2"]}</td>
            <td>{results["Cond+Prs+Sg2"]}</td>
            <td>{results["Imprt+Sg2"]}</td>
            <td>{results["Pot+Prs+Sg2"]}</td>
        </tr>
        <tr>
            <th>Sg3</th>
            <td>{results["Ind+Prs+Sg3"]}</td>
            <td>{results["Ind+Prt+Sg3"]}</td>
            <td>{results["Cond+Prs+Sg3"]}</td>
            <td>{results["Imprt+Sg3"]}</td>
            <td>{results["Pot+Prs+Sg3"]}</td>
        </tr>
        <tr>
            <th>Du1</th>
            <td>{results["Ind+Prs+Du1"]}</td>
            <td>{results["Ind+Prt+Du1"]}</td>
            <td>{results["Cond+Prs+Du1"]}</td>
            <td>{results["Imprt+Du1"]}</td>
            <td>{results["Pot+Prs+Du1"]}</td>
        </tr>
        <tr>
            <th>Du2</th>
            <td>{results["Ind+Prs+Du2"]}</td>
            <td>{results["Ind+Prt+Du2"]}</td>
            <td>{results["Cond+Prs+Du2"]}</td>
            <td>{results["Imprt+Du2"]}</td>
            <td>{results["Pot+Prs+Du2"]}</td>
        </tr>
        <tr>
            <th>Du3</th>
            <td>{results["Ind+Prs+Du3"]}</td>
            <td>{results["Ind+Prt+Du3"]}</td>
            <td>{results["Cond+Prs+Du3"]}</td>
            <td>{results["Imprt+Du3"]}</td>
            <td>{results["Pot+Prs+Du3"]}</td>
        </tr>
        <tr>
            <th>Pl1</th>
            <td>{results["Ind+Prs+Pl1"]}</td>
            <td>{results["Ind+Prt+Pl1"]}</td>
            <td>{results["Cond+Prs+Pl1"]}</td>
            <td>{results["Imprt+Pl1"]}</td>
            <td>{results["Pot+Prs+Pl1"]}</td>
        </tr>
        <tr>
            <th>Pl2</th>
            <td>{results["Ind+Prs+Pl2"]}</td>
            <td>{results["Ind+Prt+Pl2"]}</td>
            <td>{results["Cond+Prs+Pl2"]}</td>
            <td>{results["Imprt+Pl2"]}</td>
            <td>{results["Pot+Prs+Pl2"]}</td>
        </tr>
        <tr>
            <th>Pl3</th>
            <td>{results["Ind+Prs+Pl3"]}</td>
            <td>{results["Ind+Prt+Pl3"]}</td>
            <td>{results["Cond+Prs+Pl3"]}</td>
            <td>{results["Imprt+Pl3"]}</td>
            <td>{results["Pot+Prs+Pl3"]}</td>
        </tr>
        <tr>
            <th>ConNeg</th>
            <td>{results["Ind+Prs+ConNeg"]}</td>
            <td>{results["Ind+Prt+ConNeg"]}</td>
            <td>{results["Cond+Prs+ConNeg"]}</td>
            <td>{results["Imprt+ConNeg"]}</td>
            <td>{results["Pot+Prs+ConNeg"]}</td>
        </tr>
    </table>

    <br>

    <table>
        <caption>ikke personsbøyd</caption>
        <tr><td>Infinitive</td><td>{show(results, "Inf")}</td></tr>
        <tr><td>Perfect participle (PrfPrc)</td><td>{show(results, "PrfPrc")}</td></tr>
        <tr><td>Present participle (PrsPrc)</td><td>{show(results, "PrsPrc")}</td></tr>
        <tr><td>Supinum (Sup)</td><td>{show(results, "Sup")}</td></tr>
        <tr><td>Gerundium (Ger)</td><td>{show(results, "Ger")}</td></tr>
        <tr><td>Verb genetive (VGen)</td><td>{show(results, "VGen")}</td></tr>
        <tr><td>Verb Abessive (VAbess)</td><td>{show(results, "VAbess")}</td></tr>
        <tr><td>Actio Nom</td><td>{show(results, "Actio+Nom")}</td></tr>
        <tr><td>Actio Gen</td><td>{show(results, "Actio+Gen")}</td></tr>
        <tr><td>Actio Loc</td><td>{show(results, "Actio+Loc")}</td></tr>
        <tr><td>Actio Ess</td><td>{show(results, "Actio+Ess")}</td></tr>
        <tr><td>Actio Com</td><td>{show(results, "Actio+Com")}</td></tr>
    </table>

    <table>
        <caption>Gerundium</caption>
        <tr><td>Ger+PxSg1</td><td>{show(results, "Ger+PxSg1")}</td></tr>
        <tr><td>Ger+PxSg2</td><td>{show(results, "Ger+PxSg2")}</td></tr>
        <tr><td>Ger+PxSg3</td><td>{show(results, "Ger+PxSg3")}</td></tr>
        <tr><td>Ger+PxDu1</td><td>{show(results, "Ger+PxDu1")}</td></tr>
        <tr><td>Ger+PxDu2</td><td>{show(results, "Ger+PxDu2")}</td></tr>
        <tr><td>Ger+PxDu3</td><td>{show(results, "Ger+PxDu3")}</td></tr>
        <tr><td>Ger+PxPl1</td><td>{show(results, "Ger+PxPl1")}</td></tr>
        <tr><td>Ger+PxPl2</td><td>{show(results, "Ger+PxPl2")}</td></tr>
        <tr><td>Ger+PxPl3</td><td>{show(results, "Ger+PxPl3")}</td></tr>
    </table>
{:else if state === "error"}
    error
{/if}

<style>
    table {
        --border-color: rgb(150, 150, 150);
        display: inline-block;
        border: 1px solid black;
        border-radius: 4px;
        border-collapse: collapse;
        caption-side: bottom;
    }

    table tr {
        border-bottom: 1px solid var(--border-color);
    }

    table caption {
        padding: 0.5em;
        font-weight: bold;
    }

    table th.expl {
        color: rgb(80, 80, 80);
        font-style: italic;
    }

    /* TEMP */
    table th {
        border: 1px solid var(--border-color);
    }
    /* TEMP END */

    table thead tr:last-of-type {
        border-bottom: 2px solid black;
    }

    table colgroup col.ind {
        background-color: #ebeefb;
        border-left: 1px solid var(--border-color);
    }

    table colgroup col.cond {
        background-color: #f7f0db;
        border-left: 1px solid var(--border-color);
    }

    table colgroup col.imperative {
        background-color: #f9e2ce;
        border-left: 1px solid var(--border-color);
    }

    table colgroup col.potential {
        background-color: #f2e5f7;
        border-left: 1px solid var(--border-color);
    }

    table td, table th {
        padding: 14px 12px;
    }
</style>
