import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AddressService {
  private baseUrl = 'http://127.0.0.1:8000/api/addresses'; // Base URL for Django API
  private pairwiseDataKey = 'pairwiseData'; // Key for storing pairwise data in localStorage
  private solutionDataKey = 'solutionData'; // Key for storing solution data in localStorage
  private addressesKey = 'addresses'; // Key for storing addresses in localStorage

  constructor(private http: HttpClient) {}

  /**
   * Get pairwise distances from the backend with timeCategory included.
   */
  getPairwiseDistances(addresses: { id: number; address: string; timeCategory: number }[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/pairwise/`, { addresses });
  }

  /**
   * Get the optimal solution from the backend with timeCategory included.
   */
  getOptimalSolution(addresses: { id: number; address: string; timeCategory: number }[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/solution/`, { addresses });
  }

  /**
   * Store pairwise distances data in local storage.
   */
  setPairwiseData(data: { from: string; to: string; distance: string; duration: string }[]): void {
    localStorage.setItem(this.pairwiseDataKey, JSON.stringify(data));
  }

  /**
   * Retrieve pairwise distances data from local storage.
   */
  getPairwiseData(): { from: string; to: string; distance: string; duration: string }[] {
    const data = localStorage.getItem(this.pairwiseDataKey);
    return data ? JSON.parse(data) : [];
  }

  /**
   * Store optimal solution data in local storage.
   */
  setSolutionData(data: any): void {
    localStorage.setItem(this.solutionDataKey, JSON.stringify(data));
  }

  /**
   * Retrieve optimal solution data from local storage.
   */
  getSolutionData(): any {
    const data = localStorage.getItem(this.solutionDataKey);
    return data ? JSON.parse(data) : null;
  }

  /**
   * Store addresses in local storage.
   */
  setAddresses(addresses: { id: number; address: string; timeCategory?: number }[]): void {
    localStorage.setItem(this.addressesKey, JSON.stringify(addresses));
  }

  /**
   * Retrieve addresses from local storage.
   */
  getAddresses(): { id: number; address: string; timeCategory?: number }[] {
    const data = localStorage.getItem(this.addressesKey);
    return data ? JSON.parse(data) : [];
  }
}