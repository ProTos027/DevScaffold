import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/';

export const registerUser = (userData) => {
    /* use await when using fn*/
    return axios.post(`${API_URL}register_user/`, userData);
};

export const login = (credentials) => {
    /* use await when using fn*/
    return axios.post(`${API_URL}login/`, credentials);
};

export const viewConfig = () => {
    /* use await when using fn*/
    return axios.get(`${API_URL}view_config/`);
};

export const moddedConfig = (configData) => {
    /* use await when using fn*/
    return axios.post(`${API_URL}modded_config/`, configData);
};

export const viewDir = () => {
    /* use await when using fn*/
    return axios.get(`${API_URL}view_dir/`);
};

export const moddedDir = (dirData) => {
    /* use await when using fn*/
    return axios.post(`${API_URL}modded_dir/`, dirData);
};

export const getProject = () => {
    /* or use then immediately*/
    return axios({
        url: `${API_URL}get_project/`,
        method: 'GET',
        responseType: 'blob',
    }).then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'project.zip');
        document.body.appendChild(link);
        link.click();
    });
};