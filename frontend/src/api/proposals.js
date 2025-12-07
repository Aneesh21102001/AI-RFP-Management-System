import client from './client';

export const proposalsApi = {
  getAll: async (rfpId) => {
    const params = rfpId ? { rfp_id: rfpId } : {};
    const response = await client.get('/proposals', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await client.get(`/proposals/${id}`);
    return response.data;
  },

  compare: async (rfpId) => {
    const response = await client.get(`/proposals/rfp/${rfpId}/compare`);
    return response.data;
  },
};
