<script>
    import ParadigmTable from "../../ParadigmTable.svelte";
    import { Table } from "@giellatekno/tablelib";

    export let api_data;

    let error = !Array.isArray(api_data);

    let infinitive = "";

    const personsboyd_table = Table.from_format(`
          |   Indicative    | Conditional| Imperative | Potential
          |Present|Preterite| Present    |     (-)    | Present
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
        { caption: "Personsbøyd" },
    );

    const gerundium_table = Table.from_format( `
        Gerundium (Ger)   |
        PxSg1             |
        PxSg2             |
        PxSg3             |
        PxDu1             |
        PxDu2             |
        PxDu3             |
        PxPl2             |
        PxPl1             |
        PxPl3             |
        `,
        { caption: "Gerundium" },
    );

    const other_table = Table.from_format(`
        Infinitive                  |
        Perfect participle (PrfPrc) |
        Present participle (PrsPrc) |
        Supinum (Sup)               |
        Verb genetive (VGen)        |
        Verb Abessive (VAbess)      |
        Actio Nom                   | 
        Actio Gen                   | 
        Actio Loc                   | 
        Actio Ess                   | 
        Actio Com                   | 
    `);

    if (error) {
        console.error("sme/V.svelte: api_data not an array");
    } else {
        for (const [line, res] of api_data) {
            const splits = line.split("+");
            if (splits[2] === "Inf") {
                infinitive = res;
                continue;
            }

            const [ table, row, col ] = find_table_and_coords(line);
            if (table && row >= 0 && col >= 0) {
                table.data
                    .get(row, col)
                    .and_modify(s => `${s}, ${res}`)
                    .or_insert(res);
            }
        }
    }

    function find_table_and_coords(line) {
        const splits = line.split("+");
        const last = splits.at(-1).trim();
        if (splits[2] === "Inf") {
            return [ null, -1, -1 ];
        }

        const person_row = personsboyd_table.row_headers.indexOf(last);
        if (person_row >= 0) {
            let col = -1;
            switch (splits[2]) {
                case "Ind":
                    // Prs col 0, Prt col 1 (we assume Prt if not Prs)
                    col = splits[3] === "Prs" ? 0 : 1;
                    break;
                case "Cond": col = 2; break;
                case "Imprt": col = 3; break;
                case "Pot": col = 4; break;
            }
            if (col >= 0) {
                return [ personsboyd_table, person_row, col ];
            }
        }

        const ger_index = splits.findIndex(spl => spl === "Ger");
        if (ger_index >= 0) {
            if (splits.length === ger_index + 1) {
                // the "plain" form has no other tags after Ger, so
                // the "Ger" is at the last index, i.e. if it's at 2,
                // the length is 3
                return [ gerundium_table, 0, 0 ];
            } else {
                // otherwise, the specifier tag is immediately following it,
                // as the last tag (at index -1) 
                const row = gerundium_table.row_headers.indexOf(last);
                return [ gerundium_table, row, 0 ];
            }
        }

        // the remaining items go in it's own table.
        switch (splits[2]) {
            case "Inf": return [ other_table, 0, 0 ];
            case "PrfPrc": return [ other_table, 1, 0 ];
            case "PrsPrc": return [ other_table, 2, 0 ];
            case "Sup": return [ other_table, 3, 0 ];
            case "VGen": return [ other_table, 4, 0 ];
            case "VAbess": return [ other_table, 5, 0 ];
            case "Actio":
                switch (splits[3]) {
                    case "Nom": return [ other_table, 6, 0 ];
                    case "Gen": return [ other_table, 7, 0 ];
                    case "Loc": return [ other_table, 8, 0 ];
                    case "Ess": return [ other_table, 9, 0 ];
                    case "Com": return [ other_table, 10, 0 ];
                }
                break;
            default:
                console.error("unhandled line:", splits);
        }

        return [ null, -1, -1 ];
    }
</script>

<h2>Verb: {infinitive}</h2>

{#if error}
    <p>Noe har gått galt</p>
{:else}
    <ParadigmTable table={personsboyd_table} />
    <ParadigmTable table={gerundium_table} />
    <ParadigmTable table={other_table} />
{/if}
