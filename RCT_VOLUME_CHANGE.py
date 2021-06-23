if __name__ == "__main__":

	file_pre = open("./results/pre-scan-results.txt","r")
	file_post = open("./results/post-scan-results.txt","r")
	
	pre_scan_vol = float(file_pre.readline())
	post_scan_vol = float(file_post.readline())
	
	vol_change = post_scan_vol - pre_scan_vol
	percent_change = (vol_change*100)/pre_scan_vol
	
	file_pre.close()
	file_post.close()

	print("**********************************")
	print("TOTAL TOOTH RCT VOLUME CHANGE: "+ str(vol_change) + " cubic microns")
	print("TOTAL TOOTH RCT VOLUME PERCENTAGE CHANGE: "+ str(percent_change) + " %")
	print("**********************************")

	file = open("./results/final-scan-results.txt","w")
	L = ["Volume Change ="+str(vol_change), " | Percentage Volume Change ="+str(percent_change)]
	file.writelines(L) 
	file.close()