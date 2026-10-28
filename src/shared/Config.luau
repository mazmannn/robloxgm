--!strict
-- Technical test values only. Game balance and pet species are not approved yet.
return table.freeze({
    SchemaVersion = 1,
    TeamLimit = 3,
    CollectionLimit = 100,
    RequestInterval = 0.15,
    StarterSpeciesId = "prototype",
    Species = table.freeze({ prototype = true }),
})
