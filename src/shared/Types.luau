--!strict
export type Pet = {
    Id: string,
    SpeciesId: string,
    Form: number,
    Level: number,
}
export type Profile = {
    SchemaVersion: number,
    Resources: { Crystals: number, UpgradeMaterial: number, RareMaterial: number },
    Pets: { [string]: Pet },
    EquippedPetIds: { string },
}
export type Session = { Task: "Idle" }
export type Snapshot = {
    storageMode: "MemoryOnly",
    profile: Profile,
    session: Session,
}
export type Request =
    { action: "GetState" | "RecallTeam" }
    | { action: "EquipPet" | "UnequipPet", petId: string }
export type Response = { ok: boolean, code: string, state: Snapshot? }
return {}
