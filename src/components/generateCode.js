function findRemoteFunc (list, funcList, tokenFuncList, blankList) {
  for (let i = 0; i < list.length; i++) {
    if (list[i].type == 'grid') {
      list[i].columns.forEach(item => {
        findRemoteFunc(item.list, funcList, tokenFuncList, blankList)
      })
    } else {
      if (list[i].type == 'blank') {
        if (list[i].model) {
          blankList.push({
            name: list[i].model,
            label: list[i].name
          })
        }
      } else if (list[i].type == 'imgupload') {
        if (list[i].options.tokenFunc) {
          tokenFuncList.push({
            func: list[i].options.tokenFunc,
            label: list[i].name,
            model: list[i].model
          })
        }
      } else {
        if (list[i].options.remote && list[i].options.remoteFunc) {
          funcList.push({
            func: list[i].options.remoteFunc,
            label: list[i].name,
            model: list[i].model
          })
        }
      }
    }
  }
}

export default function (data) {

  const funcList = []

  const tokenFuncList = []

  const blankList = []

  findRemoteFunc(JSON.parse(data).list, funcList, tokenFuncList, blankList)

  let funcTemplate = ''

  let blankTemplate = ''

  for(let i = 0; i < funcList.length; i++) {
    funcTemplate += `
            ${funcList[i].func} (resolve) {
              // ${funcList[i].label} ${funcList[i].model}
              // Call callback function once get the data from remote server
              // resolve(data)
            },
    `
  }

  for(let i = 0; i < tokenFuncList.length; i++) {
    funcTemplate += `
            ${tokenFuncList[i].func} (resolve) {
              // ${tokenFuncList[i].label} ${tokenFuncList[i].model}
              // Call callback function once get the token
              // resolve(token)
            },
    `
  }

  for (let i = 0; i < blankList.length; i++) {
    blankTemplate += `
        <template slot="${blankList[i].name}" slot-scope="scope">
          <!-- ${blankList[i].label} -->
          <!-- use v-model="scope.model.${blankList[i].name}" to bind data -->
        </template>
    `
  }

  return `<!DOCTYPE html>
  <html>
  <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1" /> 
  <title>智能表单 (Form)</title>
    <link rel="stylesheet" href="https://unpkg.com/element-ui/lib/theme-chalk/index.css">
    <link rel="stylesheet" href="https://unpkg.com/form-making/dist/FormMaking.css">
	<link rel="stylesheet" href="static/github.css" /> 
 </head> 
 <body> 
  <article class="markdown-body">
    <div id="app">
      <fm-generate-form :data="jsonData" :remote="remoteFuncs" :value="editData" ref="generateForm">
        
      </fm-generate-form>
      <el-button type="primary" @click="handleSubmit" :disabled="disable">提交</el-button>
    </div>
  </article>  
    <script src="https://unpkg.com/vue/dist/vue.js"></script>
	<script src="https://unpkg.com/axios@0.19.1/dist/axios.min.js"></script>
    <script src="https://unpkg.com/element-ui/lib/index.js"></script>
    <script src="https://unpkg.com/form-making/dist/FormMaking.umd.js"></script>
    <script>
      new Vue({
        el: '#app',
        data: {
          jsonData: ${data},
          editData: {},
          remoteFuncs: {
            ${funcTemplate}
          },
		  disable: false
        },
        methods: {
          handleSubmit () {
            this.$refs.generateForm.getData().then(data => {
              // data check success
              // data - form data
			
			axios({  
				method:'post',  
				url:'http://127.0.0.1:5000/fillin',  
				data:{
					firstName: 'mytest',
					widgetForm: data
					},  
				headers:{'Content-Type': 'application/json'} 
			}).then((res)=>{
				this.disable = true;
				console.log(res.data);
			});					  
			  
            }).catch(e => {
              // data check failed
            })
          }
        }
      })
    </script>
  </body>
  </html>`
}