<script>
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";

    export let table;

    const TAG_TO_ENGLISH = {
        Inf: "Infinitive",
        Ind: "Indicative",
        Cond: "Conditional",
        Imprt: "Imperative",
    };


    console.log(table.as_console_str());
    table = table.without_empty_columns_and_rows();
    console.log(table.as_console_str());

    /*
    function show(obj, key) {
        const res = obj[key];
        return res === undefined ? "-" : res;
    }
    */
</script>

{#if table}
    <table>
        {#if table.caption}
            <caption>{table.caption}</caption>
        {/if}
        <thead>
            {#each table.column_headers as column_row}
                <tr>
                    {#if table.row_headers}
                        <th></th>
                    {/if}
                    {#each column_row as { text, span }}
                        {#if text.trim() !== "-"}
                            <th colspan={span}>{text}</th>
                        {/if}
                    {/each}
                </tr>
            {/each}
        </thead>
        <tbody>
            {#each table.data.rows as row, i}
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
{/if}

<!--
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

-->

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
