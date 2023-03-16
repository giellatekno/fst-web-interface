<script>
    import { throttle_time } from "./../../../lib/utils.js";
    import ParadigmTable from "../../ParadigmTable.svelte";
    import { Table } from "@giellatekno/tablelib";

    export let api_data;

    let error = !Array.isArray(api_data);

    const table1 = Table.from_format(`
            | Sg | Pl
        Nom |
        Gen |
        Loc |
        Acc |
        Com |
        Ill |
        `,
        { caption: "Table1" },
    );

    function on_resize() {
    }
</script>

<svelte:window on:resize={throttle_time(500)(on_resize)} />

<h2>Noun: </h2>

{#if error}
    <p>Noe har gått galt</p>
{:else}
    {#each api_data as d}
        <p>{d}</p>
    {/each}
{/if}
