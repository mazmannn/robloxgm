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
export type Session = { Task: "Idle" | "Mining" | "Combat" }
export type Snapshot = {
    storageMode: "MemoryOnly",
    profile: Profile,
    session: Session,
    mining: {targetId: string?, nodes: {[string]: {health: number, readyAt: number}}}?,
    combat: {enemyHP: number,active: boolean,pets: {[string]: {hp: number,readyAt: number}}}?,
    merchant: {page: string?,offers: {any}}?,
    playerHealth: {hp: number,max: number}?,
}
export type Request =
    { action: "GetState" | "RecallTeam" }
    | { action: "EquipPet" | "UnequipPet", petId: string }
    | { action: "SelectTarget", nodeId: string }
    | { action: "AttackEnemy" | "TalkMerchant" | "TradeMerchant" | "LeaveMerchant" }
export type Response = { ok: boolean, code: string, state: Snapshot? }
return {}
