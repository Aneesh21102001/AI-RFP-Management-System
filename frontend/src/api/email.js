import client from './client';

export const emailApi = {
  sendRFP: async (request) => {
    const response = await client.post('/email/send-rfp', request);
    return response.data;
  },

  receiveEmail: async (request) => {
    const response = await client.post('/email/receive', request);
    return response.data;
  },
};
