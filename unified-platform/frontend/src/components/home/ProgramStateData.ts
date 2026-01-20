
export interface ProgramAvailability {
    state: string;
    commercial: boolean;
    hardMoney: boolean;
    businessPurpose: boolean;
    conventional: boolean;
}

// Data matching the production screenshot "All Programs By State"
// "AVAILABLE" means true, empty means false
export const PROGRAM_AVAILABILITY_DATA: ProgramAvailability[] = [
    { state: 'ALABAMA', commercial: true, hardMoney: true, businessPurpose: false, conventional: false },
    { state: 'ALASKA', commercial: true, hardMoney: true, businessPurpose: true, conventional: false },
    { state: 'ARIZONA', commercial: true, hardMoney: true, businessPurpose: true, conventional: true },
    { state: 'ARKANSAS', commercial: true, hardMoney: true, businessPurpose: true, conventional: false },
    { state: 'CALIFORNIA', commercial: true, hardMoney: true, businessPurpose: true, conventional: true },
    { state: 'COLORADO', commercial: true, hardMoney: true, businessPurpose: true, conventional: true },
    { state: 'CONNECTICUT', commercial: true, hardMoney: true, businessPurpose: true, conventional: false },
    { state: 'DELAWARE', commercial: true, hardMoney: true, businessPurpose: true, conventional: false },
    { state: 'FLORIDA', commercial: true, hardMoney: true, businessPurpose: true, conventional: true },
    { state: 'GEORGIA', commercial: true, hardMoney: true, businessPurpose: true, conventional: true },
    { state: 'HAWAII', commercial: true, hardMoney: true, businessPurpose: true, conventional: true },
    { state: 'IDAHO', commercial: true, hardMoney: true, businessPurpose: false, conventional: false },
    { state: 'ILLINOIS', commercial: true, hardMoney: true, businessPurpose: true, conventional: false },
    { state: 'INDIANA', commercial: true, hardMoney: true, businessPurpose: true, conventional: false },
    { state: 'IOWA', commercial: true, hardMoney: true, businessPurpose: true, conventional: false },
];
