PRAGMA synchronous = OFF;
PRAGMA journal_mode = MEMORY;
PRAGMA locking_mode = EXCLUSIVE;
PRAGMA cache_size = -100000; -- 100MB cache


-- Add indexes on queried table.
CREATE INDEX USR02_idx ON USR02(MANDT, BNAME, UFLAG, ZBVMASTER);
CREATE INDEX UST10C_idx ON UST10C(MANDT, PROFN, SUBPROF);
CREATE INDEX UST10S_idx on UST10S(MANDT, PROFN, AUTH, OBJCT, AKTPS);
CREATE INDEX UST04_idx ON UST04(MANDT, PROFILE, BNAME);
CREATE INDEX UST12_idx ON UST12(MANDT, OBJCT, AUTH, FIELD, VON, BIS);

-- This table contains authorizations objects assigned to a "real" profile.
-- It skips the distinction of single and composite profiles. 
CREATE TABLE D_USER_PROFILES(MANDT INT, ROOTPROFN TEXT, OBJCT TEXT, AUTH TEXT);

-- Insert all single profiles.
INSERT INTO D_USER_PROFILES (MANDT, ROOTPROFN, OBJCT, AUTH)
SELECT MANDT, PROFN, OBJCT, AUTH FROM UST10S 
	WHERE UST10S.AKTPS = 'A' AND EXISTS (SELECT 1 FROM UST04 WHERE UST04.MANDT = UST10S.MANDT AND UST04.PROFILE = UST10S.PROFN);

-- Insert all composite profiles with their equivalent single profiles.
INSERT INTO D_USER_PROFILES (MANDT, ROOTPROFN, OBJCT, AUTH)
WITH RECURSIVE
	ALL_PROFILES(MANDT, ROOTPROFN, PROFN) AS (
		-- Base case: all composite profiles assigned to at least one user.
 		SELECT MANDT, PROFN, SUBPROF FROM UST10C 
			WHERE UST10C.AKTPS = 'A' AND EXISTS (SELECT 1 FROM UST04 WHERE UST04.MANDT = UST10C.MANDT AND UST04.PROFILE = UST10C.PROFN)
		UNION ALL 
			-- Recursive case: subprofiles may be composite or single.
			SELECT ALL_PROFILES.MANDT, ROOTPROFN, SUBPROF 
			FROM ALL_PROFILES 
			INNER JOIN UST10C USING(MANDT, PROFN)
	)
SELECT UST04.MANDT, ROOTPROFN, OBJCT, AUTH
	FROM 
		ALL_PROFILES
		-- Only keep single profiles, i.e. the leaves of the tree with ROOTPROFN as the root.
		INNER JOIN UST10S USING(MANDT, PROFN) 
		-- Only keep assigned root profiles. Is technically redundant because of our base case. 
		-- All root profiles are already assigned. However, we need to retrieve the BNAME.
		INNER JOIN UST04 ON ROOTPROFN = UST04.PROFILE AND ALL_PROFILES.MANDT = UST04.MANDT 
	WHERE AKTPS = 'A'; 

-- We duplicate data instead of using a view to be able to use an index.
CREATE TABLE PROFILE_AUTHS AS
	SELECT MANDT, ROOTPROFN, OBJCT, AUTH, FIELD, VON, BIS
		FROM 
			D_USER_PROFILES 
			INNER JOIN UST12 USING(MANDT, OBJCT, AUTH);
		-- WHERE
		-- 	EXISTS(
		-- 		SELECT 1 FROM USR02 
		-- 		WHERE USR02.MANDT = D_USER_PROFILES.MANDT 
		-- 		AND USR02.BNAME = D_USER_PROFILES.BNAME 
		-- 		AND ZBVMASTER != 'X' -- Accounts with this attribute set cannot login.
		-- 		AND UFLAG = '0' -- UFLAG=0: User not locked. other values means that the user is locked.
		-- 	) AND AKTPS = 'A'; 

-- Optimization: Add an index for faster lookup.
CREATE INDEX PROFILE_AUTHS_index ON PROFILE_AUTHS(MANDT, OBJCT, AUTH, FIELD, VON);

-- We don't need this table anymore.
DROP TABLE IF EXISTS D_USER_PROFILES;