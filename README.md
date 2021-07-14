## 在 Enclave 中进行创建密钥，并利用密钥完成随机数加解密

## Diagram

![Architecture](./docs/assets/Architecture.png)

**注意：该Demo运行在ap-northeast-1区域**
1. 新建支持enclave功能的ec2 instance  
2. 安装nitro-cli包  
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
git clone -b decrypt_cli https://github.com/hxhwing/Nitro-Enclave-Demo.git
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
请记录下您的```EnclaveCID```以及PCR0

8. 进入[KMS界面](https://ap-northeast-1.console.aws.amazon.com/kms/home?region=ap-northeast-1#/kms/keys),创建key
  采取默认的方法生成key，定义密钥使用权限使用ec2相同的IAM，生成完毕后修改policy如下：
  INSTANCE_ROLE_ARN与您EC2instance的instance一样
  ```bash 
  {
    "Version": "2012-10-17",
    "Id": "key-consolepolicy-3",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": KMS_ADMINISTRATOR_ROLE
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow access for Key Administrators",
            "Effect": "Allow",
            "Principal": {
                "AWS": INSTANCE_ROLE_ARN
            },
            "Action": [
                "kms:Create*",
                "kms:Describe*",
                "kms:Enable*",
                "kms:List*",
                "kms:Put*",
                "kms:Update*",
                "kms:Revoke*",
                "kms:Disable*",
                "kms:Get*",
                "kms:Delete*",
                "kms:TagResource",
                "kms:UntagResource",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Enable decrypt from enclave",
            "Effect": "Allow",
            "Principal": {
                "AWS": INSTANCE_ROLE_ARN
            },
            "Action": "kms:Decrypt",
            "Resource": "*",
            "Condition": {
                "StringEqualsIgnoreCase": {
                    "kms:RecipientAttestation:ImageSha384": PCR0_VALUE_FROM_EIF_BUILD
                }
            }
        },
        {
            "Sid": "Enable encrypt from instance",
            "Effect": "Allow",
            "Principal": {
                "AWS": INSTANCE_ROLE_ARN
            },
            "Action": "kms:Encrypt",
            "Resource": "*"
        }
    ]
}
```
生成万密钥后记录下您的 **keyid**

9. 再打开一个instance 窗口，运行**vsock-proxy** 工具  
```bash
vsock-proxy 8000 kms.ap-northeast-1.amazonaws.com 443  
```   

10. 进入client文件夹    
```
cd Nitro-Enclave-Demo/client    
```

11. 下载相关包并运行文件     
```bash     
yum install python3 -y
python3 -m venv venv
source venv/bin/activate
sudo pip3 install -r requirements.txt
sudo python3 client.py [EnclaveCID] [KEY_ID]
```
结果如下：
```bash
{'Plaintext': b'811505', 'Ciphertext': b"\x01\x02\x02\x00x\xae\x83ysZ\xfch%\x1a\x0b\x1d,%`\xec\x7f\x1a\x08>\xcfO\x9f\x98\xcah\xa9\xd9\xacb\xa6\x8e\x8e\x01\xe8xR<9.\xa3\xed\xcb\xd8PX0!W\xa4\x00\x00\x00d0b\x06\t*\x86H\x86\xf7\r\x01\x07\x06\xa0U0S\x02\x01\x000N\x06\t*\x86H\x86\xf7\r\x01\x07\x010\x1e\x06\t`\x86H\x01e\x03\x04\x01.0\x11\x04\x0c\xdc2\x15o\x9c\x0fq\x050\x8eW\xf0\x02\x01\x10\x80!w\xadV\xa6<7O\xf5o\xf3\xd1\x96\xc45\xa0\xf2n~gX'>B#\xf8\xf1o@f.X\x0e\xd6", 'Encrypted-Plaintext': '811505', 'Encrypted2': '811505'}
```