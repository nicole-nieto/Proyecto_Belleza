/* static/js/app.js
   Utilidades globales: gestión de sesión, fetch con token y control de nav.
   Funciona sin modules. */

(function(){
    const IS_LOCAL = location.hostname==='localhost'||location.hostname==='127.0.0.01';
    const LOCAL_API='http://localhost:8000';
    window.API_BASE=IS_LOCAL?LOCAL_API:'';

    // SESSION
    window.saveSession=function(token,rol){localStorage.setItem('token',token);localStorage.setItem('rol',rol||'');};
    window.getToken=function(){return localStorage.getItem('token');};
    window.getRol=function(){return localStorage.getItem('rol');};
    window.clearSession=function(){localStorage.removeItem('token');localStorage.removeItem('rol');};

    // fetch con token + manejo 401
    window.apiFetch=async function(path,options={}) {
        const token=window.getToken();
        const headers=options.headers||{};
        if(!(options.body instanceof FormData)){
            if(!headers['Content-Type']&&!headers['content-type']) headers['Content-Type']='application/json';
            if(options.body&&typeof options.body==='object') options.body=JSON.stringify(options.body);
        }
        if(token) headers['Authorization']='Bearer '+token;
        const final=Object.assign({},options,{headers});
        const url=window.API_BASE+path;
        let resp;
        try{resp=await fetch(url,final);}catch(err){throw new Error('network');}
        if(resp.status===401){window.clearSession();if(location.pathname!='/login') location.href='/login';throw new Error('unauthorized');}
        return resp;
    };

    // Nav: mostrar/ocultar botones de login/logout
    function updateNav(){
        const btnLogout=document.getElementById('btn-logout');
        const navLogin=document.getElementById('nav-login');
        if(!btnLogout||!navLogin) return;
        if(window.getToken()){btnLogout.classList.remove('hidden');navLogin.classList.add('hidden');}
        else{btnLogout.classList.add('hidden');navLogin.classList.remove('hidden');}
    }

    // logout handler
    document.addEventListener('DOMContentLoaded',function(){
        const btnLogout=document.getElementById('btn-logout');
        if(btnLogout) btnLogout.addEventListener('click',function(){window.clearSession();location.href='/login';});
        updateNav();
    });
})();
