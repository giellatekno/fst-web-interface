<script>
    //import ParadigmTable from "../../ParadigmTable.svelte";
    //import { Table } from "@giellatekno/tablelib";

    export let api_data;

    let error = !Array.isArray(api_data);
</script>

<h2>...</h2>

{#if error}
    <p>Noe har gått galt</p>
    <p>{JSON.stringify(api_data)}</p>
{:else}
    {#each api_data as d}
        <p>{d}</p>
    {/each}
{/if}
