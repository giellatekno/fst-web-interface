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

    class TableBuilder {
        constructor() {
            this.size_x = 0;
            this.size_y = 0;
            this._row_headers = [];
            this._column_headers = null;
            this._caption = "";
        }

        column_headers(headers) {
            if (this._column_headers === null) {
                this._column_headers = [[...headers]];
            } else {
                if (headers.length !== this._column_headers[0].length) {
                    throw Error("incorrect number of args");
                }
                this._column_headers.push(headers);
            }
            return this;
        }

        row_headers(headers) { this._row_headers.push(headers); return this; }
        caption(text) { this._caption = text; return this; }

        build() {
            this.data = Array(this.size_y);
            for (let i = 0; i < this.size_y; i++) {
                this.data[i] = Array(this.size_x).fill(null).map(_0 => new Entry());
            }
            this._ready = true;
            return new Table(this);
        }
    }

    class Table {
        constructor(builder) {
            this.size_x = builder.size_x;
            this.size_y = builder.size_y;
            this.row_headers = builder._row_headers;
            this.column_headers = builder._column_headers;
            this.data = builder.data;
        }

        entry(row, col) {
            return this.data[row][col];
        }

        find_row_by_header(header) {
            return this.row_headers.indexOf(header);
        }

        find_column_by_headers(...headers) {
            console.log("find_column_by_headers()")
            console.log(headers);
            const indexes = [];
            let i = 0;
            for (let A of headers) {
                console.log("A");
                console.log(A);
                const B = this.column_headers[i];
                console.log("B");
                console.log(B);

                if (A === B) {
                    indexes.push(i);
                } else {
                    // scan array
                    console.log("we need to scan array");
                }

                i++;
            }

            return 
        }

        find_entry_by_headers(row_header, column_header1, column_header2) {
            const row = this.row_headers.indexOf(row_header);
            if (row === -1) return [-1, -1];

            const col1 = this.column_headers[0].indexOf(column_header1);
            const col2 = this.column_headers[1].indexOf(column_header2);

            return this.data[row][col2];
        }
    }

    class VerbTables {
        constructor(data) {
            this.personsboyd = new TableBuilder()
                .caption("Personsbøyd")
                .row_headers(["Sg1", "Sg2", "Sg3", "Du1", "Du2", "Du3", "Pl1", "Pl2", "Pl3"])
                .column_headers(["Mood", "Ind", "Cond", "Imprt", "Pot"])
                .column_headers(["Tense", ["Present", "Preterite"], "Present", "", "Present"])
                .build();

            this.gerundium = new TableBuilder()
                .caption("Gerundium")
                .row_headers([
                    "Ger+PxSg1", "Ger+PxSg2", "Ger+PxSg3", "Ger+PxDu1",
                    "Ger+PxDu2", "Ger+PxDu3", "Ger+PxPl1", "Ger+PxPl2",
                    "Ger+PxPl3",
                ])
                .build();
            
            this.misc = new TableBuilder()
                .row_headers([
                    "Inf", "PrfPrc", "PrsPrc", "Sup", "Ger", "VGen",
                    "VAbess", "Actio+Nom", "Actio+Gen", "Actio+Loc",
                    "Actio+Ess", "Actio+Com",
                ])
                .build();

            this.d = {};
            for (let [line, word] of data.result) {
                const splits = line.split("+").slice(2);
                const first = splits[0];
                const rest = splits.slice(1);
                const last = splits.at(-1);

                // which table should this go into?
                if (this.personsboyd.row_headers.includes(last)) {
                    const row = this.personsboyd.find_row_by_header(first);
                    const col = this.personsboyd.find_column_by_headers(...rest);
                    this.personsboyd.entry(row, col).set_text(word);
                }
            }
            console.log("personsbøyd");
            console.log(this.personsboyd.data);
        }

        add(field, data) {
            const splits = field.split("+").slice(2);

            let cur = this.d;
            for (let split of splits) cur = cur[split] = cur[split] || {};
            if (!Array.isArray(cur.data)) cur.data = [];
            cur.data.push(data);
        }

        columns() {
            const c = new Set(Object.keys(this.d));
            for (let [k, v] of Object.entries(this.d)) {
                if ("data" in v) {
                    c.delete(k);
                }
            }
            console.log("columns");
            console.log(Array.from(c.keys()));
        }
    }

    function parse_data(data) {
        const vt = new VerbTables(data);
        vt.columns();

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
