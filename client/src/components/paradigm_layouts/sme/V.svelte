<script>
    import ParadigmTable from "../../ParadigmTable.svelte";
    import { Table } from "../../../lib/table.js";

    // assume array?
    export let api_data;

    console.log("sme/V.svelte: api_data");
    console.log(api_data);

    const personsboyd_table = Table.from_format(
        `
     -|   Indicative    |Conditional|Imperative | Potential | x
     -|Present|Preterite|Present    |           | Present   | x
   Sg1|
   Sg2|
   Sg3|
   Du1|
   Du2|
   Du3|
   Pl1|
   Pl2|
   Pl3|
ConNeg|
        `,
        "Personsbøyd",
    );

    const gerundium_table = Table.from_format(
        `
        Infinitive                  |
        Perfect participle (PrfPrc) |
        Present participle (PrsPrc) |
        Supinum (Sup)               |
        Gerundium (Ger)             |
        Verb genetive (VGen)        |
        Verb Abessive (VAbess)      |
        Actio Nom                   | 
        Actio Gen                   | 
        Actio Loc                   | 
        Actio Ess                   | 
        Actio Com                   | 
        `,
        "Gerundium",
    );

    if (Array.isArray(api_data)) {
        for (const [line, res] of api_data) {
            const splits = line.split("+");
            const last = splits.at(-1).trim();


            // see if it's in the "personsbøyd" table
            const row_idx = personsboyd_table.row_headers.indexOf(last);
            let col_idx;

            // find column index
            switch (splits[2]) {
                case "Ind":
                    if (splits[3] === "Prs") {
                        col_idx = 0;
                    } else if (splits[3] === "Prt") {
                        col_idx = 1;
                    }
                    break;
                case "Cond":
                    col_idx = 2;
                    break;
                case "Imprt":
                    col_idx = 3;
                    break;
                case "Pot":
                    col_idx = 4;
                    break;
                default:
                    col_idx = -1;
            }

            if (row_idx >= 0 && col_idx >= 0) {
                // it belongs in the personsbøyd table
                personsboyd_table.data.set(row_idx, col_idx, res);
            }
        }
    } else {
        console.log("sme/V.svelte: api_data is an object, not an array");
    }
</script>

<h2>Verb</h2>

<ParadigmTable table={personsboyd_table} />

<ParadigmTable table={gerundium_table} />
