******************************************************************
*  COPYBOOK  : GFCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : CT
******************************************************************
 01  RT-FCT-RATING.

          03 RT-FCT-TERRITORY-CODE            PIC X(3).
          03 RT-FCT-CLASS-CODE                PIC X(4).
          03 RT-FCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FCT-RATED-PREMIUM             PIC 9(9)V9(2).
