******************************************************************
*  COPYBOOK  : GFNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : NV
******************************************************************
 01  RT-FNV-RATING.

          03 RT-FNV-TERRITORY-CODE            PIC X(3).
          03 RT-FNV-CLASS-CODE                PIC X(4).
          03 RT-FNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FNV-RATED-PREMIUM             PIC 9(9)V9(2).
