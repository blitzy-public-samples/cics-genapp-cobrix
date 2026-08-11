******************************************************************
*  COPYBOOK  : GFMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : MD
******************************************************************
 01  RT-FMD-RATING.

          03 RT-FMD-TERRITORY-CODE            PIC X(3).
          03 RT-FMD-CLASS-CODE                PIC X(4).
          03 RT-FMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FMD-RATED-PREMIUM             PIC 9(9)V9(2).
