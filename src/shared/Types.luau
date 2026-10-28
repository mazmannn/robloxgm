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
export type Session = { Task: "Idle" | "Mining" }
export type Snapshot = {
    storageMode: "MemoryOnly",
    profile: Profile,
    session: Session,
    mining: {targetId: string?, nodes: {[string]: {health: number, readyAt: number}}}?,
}
export type Request =
    { action: "GetState" | "RecallTeam" }
    | { action: "EquipPet" | "UnequipPet", petId: string }
    | { action: "SelectTarget", nodeId: string }
export type Response = { ok: boolean, code: string, state: Snapshot? }
return {}
