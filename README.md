# Nitro Enclave and Attestation Demo

## Diagram

![Architecture](./docs/assets/Architecture.png)

**注意：该Demo运行在ap-northeast-1区域**
<<<<<<< HEAD
1. 启动支持 Nitro Enclave 功能的 EC2 Instance
2. 安装 Nitro-CLI 命令行工具 
=======
1. 新建支持enclave功能的ec2 instance  
2. 安装nitro-cli包  
>>>>>>> 2158f18186f1d166e19422dce6098c4c97de9615
```bash
sudo amazon-linux-extras install aws-nitro-enclaves-cli  
sudo yum install aws-nitro-enclaves-cli-devel -y  
sudo usermod -aG ne ec2-user  
sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service  
sudo amazon-linux-extras install docker  
sudo systemctl start docker  
sudo systemctl enable docker  
sudo usermod -a -G docker ec2-user  
sudo systemctl start docker && sudo systemctl enable docker  
sudo amazon-linux-extras enable aws-nitro-enclaves-cli  
sudo yum install -y aws-nitro-enclaves-cli aws-nitro-enclaves-cli-devel   
```
3.打开/etc/nitro_enclaves/allocator.yaml，修改可分配的memory  
```bash
# memory_mib: 512  
memory_mib: 3000   
```  
4. 重新启动服务
```bash    
sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service   
sudo systemctl start docker && sudo systemctl enable docker   
```
5. Reboot 你的 instance   
```
sudo shutdown -r now
```

6. 下载代码
```bash   
yum install git    
git clone https://github.com/hxhwing/Nitro-Enclave-Demo.git
cd Nitro-Enclave-Demo/server  
```
7. 运行build.sh创建enclave image，并利用image创建enclave
```bash    
chmod +x build.sh  
sudo ./build.sh   
```   
当enclave 创建完毕，会出现  
```bash   
Enclave Image successfully created.  
{
  "Measurements": {
    "HashAlgorithm": "Sha384 { ... }",
    "PCR0": "fdd6b3c0e70ee927046ab974521362a7534a629fdccb195abc69147a133b27b8233ff9153b376af2dccf9503cb43246e",
    "PCR1": "c35e620586e91ed40ca5ce360eedf77ba673719135951e293121cb3931220b00f87b5a15e94e25c01fecd08fc9139342",
    "PCR2": "951c4c27d03d0777288f7de339abdd0640da15d454e0efbe8e29bac74a8e8ea06edda8401b6bb672b1b71d32b9bf6751"
  }
}
Start allocating memory...
Started enclave with enclave-cid: 16, memory: 2600 MiB, cpu-ids: [1, 17]
{
  "EnclaveID": "i-097a9a35e16a8962c-enc17a99614bf41bf8",
  "ProcessID": 7194,
  "EnclaveCID": 16,
  "NumberOfCPUs": 2,
  "CPUIDs": [
    1,
    17
  ],
  "MemoryMiB": 2600
}
```
请记录下您的```EnclaveCID```  

8. 再打开一个EC2 Instance 窗口，在后台运行 **vsock-proxy** 工具  
```bash
<<<<<<< HEAD
vsock-proxy 8000 kms.ap-northeast-1.amazonaws.com 443 &
=======
vsock-proxy 8000 kms.ap-northeast-1.amazonaws.com 443  
>>>>>>> 2158f18186f1d166e19422dce6098c4c97de9615
```   

9. 进入client文件夹    
```
cd Nitro-Enclave-Demo/client    
```

10. 下载相关包并运行 ```client.py```文件     
```bash     
yum install python3 -y
python3 -m venv venv
source venv/bin/activate
sudo pip3 install -r requirements.txt
sudo python3 client.py [EnclaveCID] keyId
```
  